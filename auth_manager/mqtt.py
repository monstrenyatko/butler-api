import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt
from jose import exceptions as jwt_exceptions
from . import models as local_models


log = logging.getLogger(__name__)

def getJwtDict(request):
    result = None
    auth = request.META.get('HTTP_AUTHORIZATION', None)
    if auth:
        parts = auth.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            token = parts[1]
            try:
                result = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.AUTH_JWT_ALGORITHM)
            except jwt_exceptions.ExpiredSignatureError:
                log.debug('JWT has been expired: %s', jwt.get_unverified_claims(token))
            except jwt_exceptions.JWTError as e:
                log.debug('JWT decoding error: %s', e)
            except Exception:
                log.exception('JWT decoding error')
    if result:
        log.debug('JWT payload: %s', result)
    return result

def getJwtUser(request):
    user = None
    jwtpayload = getJwtDict(request)
    if jwtpayload:
        username = jwtpayload.get('user', None)
        if username:
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                log.error('JWT user, name: %s, error: does not exist', username)
    return user

def verifyUserAccess(user):
    return user != None

def verifySuperuserAccess(user):
    return (user and user.is_superuser)

def verifyAcl(user, topic, access):
    result = False
    for acl in local_models.MqttAclModel.objects.filter(user=user):
        result = topic.startswith(acl.topic) and (
            (access == 1 and (
                acl.access == local_models.MqttAclModel.ACCESS_READ or acl.access == local_models.MqttAclModel.ACCESS_READ_WRITE
            )) or
            (access == 2 and (
                acl.access == local_models.MqttAclModel.ACCESS_WRITE or acl.access == local_models.MqttAclModel.ACCESS_READ_WRITE
            ))
        )
        if result:
            break
    return result
