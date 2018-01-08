import time
import logging
import re
import json
from django.contrib.auth import get_user_model
from django.conf import settings
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from auth_manager import models as auth_manager_models
from auth_manager import jwt as auth_manager_jwt
from ..apps import MqttManagerConfig as app_config


JWT_UPDATE_LEEWAY_SEC = 10*60
TOPICS_UPDATE_AFTER_SEC = 1*60

log = logging.getLogger(__name__)
user = None
jwt = None
jwt_exp = None
topics = None
topics_ts = None
mqtt_host = None
mqtt_client = None
db_client = None
acl_data_template_regexp = None


def convert_acl_template_to_regexp(acl_template):
    return '^' + acl_template.replace('%u', '(?P<username>.+)').replace('/', '\/') + '$'


def get_topics(acl_template_regexp):
    return [
        acl.topic
        for acl in auth_manager_models.MqttAclModel.objects.filter(user__username=user.username)
        if (   acl.access == auth_manager_models.MqttAclModel.ACCESS_READ or
               acl.access == auth_manager_models.MqttAclModel.ACCESS_READ_WRITE
           ) and acl_template_regexp.match(acl.topic)
    ]


def update_jwt():
    global jwt, jwt_exp
    log.info('Updating JWT')
    jwt = auth_manager_jwt.generate(user)
    jwt_exp = auth_manager_jwt.get_token_exp(jwt)


def update_topics():
    global topics, topics_ts, acl_data_template_regexp
    log.debug('Updating topics')
    acl_data_template = auth_manager_models.MqttAclTemplateModel.objects.get(
        name=auth_manager_models.MqttAclTemplateModel.NAME_USER_DATA
    ).template
    acl_data_template_regexp = re.compile(convert_acl_template_to_regexp(acl_data_template))
    log.debug('Topics template: %s', acl_data_template)
    topics_old = topics if topics is not None else []
    topics = get_topics(acl_data_template_regexp)
    topics_ts = int(time.time())
    return len(set(topics_old) ^ set(topics)) > 0


def is_update_required_for_jwt():
    now = int(time.time())
    return (jwt is None) or now > (jwt_exp - JWT_UPDATE_LEEWAY_SEC)


def is_update_required_for_topics():
    now = int(time.time())
    return (topics is None) or now > (topics_ts + TOPICS_UPDATE_AFTER_SEC)


def on_connect(client, userdata, flags, rc):
    log.info("Connected")
    sub_list = [(i, 0) for i in topics]
    if len(sub_list) > 0:
        client.subscribe(sub_list)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        log.warn("Unexpected disconnection. Reconnecting...")
        client.reconnect()
    else :
        log.info("Disconnected")


def on_subscribe(client, userdata, mid, granted_qos):
    log.info("Subscribed")


def make_points(username, message):
    points = []
    if message.get('v') == 1:
        data = message.get('data')
        if data:
            for measurement in data:
                key = next(iter(measurement))
                m = settings.MEASUREMENTS.get(str(key).upper())
                if m:
                    v = measurement[key]
                    if isinstance(v, int) or isinstance(v, float):
                        points.append({
                            'measurement': m,
                            'fields': {
                                'value': float(v)
                            }
                        })
                    else:
                        log.warn('[%s] Unsupported value type: %s [%s]', username, v, type(v))
                else:
                    log.warn('[%s] Unsupported measurement type: %s, please add the upper-case mapping '
                             'to the settings.MEASUREMENTS dictionary', username, key)
        else:
            log.warn('[%s] No data provided', username)
    else:
        log.warn('[%s] Unsupported version: %s', username, message.get('v'))
    return points


def on_message(client, userdata, message):
    m = acl_data_template_regexp.match(message.topic)
    if m:
        username = acl_data_template_regexp.match(message.topic).group('username')
        user = get_user_model().objects.select_related('profile').get(username=username)
        tags = {
            'location': user.profile.location.name,
            'region': user.profile.region.name,
        }
        points = make_points(user.username, json.loads(message.payload))
        log.debug('[%s] Points: %s, Tags: %s', user.username, points, tags)
        if points:
            db_client.write_points(points=points, tags=tags)


def init_data_recorder(host):
    global user, db_client, mqtt_host, mqtt_client
    mqtt_host = host
    log.info('Broker host: %s', mqtt_host)
    #
    user = get_user_model().objects.get(username=app_config.USERNAME_DATA_RECORDER)
    db_settings = settings.DATABASES['time-series']
    db_client = InfluxDBClient(
        host=db_settings['HOST'],
        port=db_settings['PORT'],
        username=db_settings['USER'],
        password=db_settings['PASSWORD'],
        database=db_settings['NAME'],
    )
    mqtt_client = mqtt.Client(client_id=user.username)
    mqtt_client.enable_logger(log.getChild('mqtt_client'))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_subscribe = on_subscribe
    mqtt_client.on_message = on_message


def stop_data_recorder():
    mqtt_client.disconnect()
    mqtt_client.loop_stop()


loop_connect = True
def loop_data_recorder():
    global loop_connect
    if is_update_required_for_topics():
        if update_topics():
            log.info('Topics have been updated')
            if not loop_connect:
                mqtt_client.reconnect()
        log.debug('Topics: %s', topics)
    if is_update_required_for_jwt():
        update_jwt()
        mqtt_client.username_pw_set(username=jwt, password='none')
        if not loop_connect:
            mqtt_client.reconnect()
    if loop_connect:
        mqtt_client.connect(mqtt_host)
        mqtt_client.loop_start()
        loop_connect = False
    return True
