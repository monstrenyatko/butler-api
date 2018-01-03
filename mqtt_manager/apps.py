import sys
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.apps import AppConfig


class MqttManagerConfig(AppConfig):
    name = 'mqtt_manager'
    verbose_name = 'mqtt manager'

    USERNAME_DATA_RECORDER = 'mqtt_data_recorder'

    def ready(self):
        if not ('makemigrations' in sys.argv or 'migrate' in sys.argv):
            UserModel = get_user_model()
            if not UserModel.objects.filter(username=self.USERNAME_DATA_RECORDER).exists():
                user = UserModel(username=self.USERNAME_DATA_RECORDER, password=make_password(None))
                user.save()
