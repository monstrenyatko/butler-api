import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt
from jose import exceptions as jwt_exceptions


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
                log.debug('JWT has been expired: {}'.format(jwt.get_unverified_claims(token)))
            except jwt_exceptions.JWTError as e:
                log.debug('JWT decoding error: {}'.format(e))
            except Exception:
                log.exception('JWT decoding error')
    if result:
        log.debug('JWT payload: {}'.format(result))
    return result

def getJwtUser(jwtpayload):
    user = None
    if jwtpayload:
        username = jwtpayload.get('user', None)
        log.debug('JWT user, name: {}'.format(username))
        if username:
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                log.error('JWT user, name: {}, error: does not exist'.format(username))
    return user

def getUser(request):
    return getJwtUser(getJwtDict(request))

def checkMqttUser(request):
    return getUser(request) != None

def checkMqttSuperuser(request):
    user = getUser(request)
    return (user and user.is_superuser)
