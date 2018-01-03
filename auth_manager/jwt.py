import time
import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from jose import jwt
from jose import exceptions as jwt_exceptions


log = logging.getLogger(__name__)


def get_dict(request):
    """ Parses the `bearer` value of the HTTP Authorization header """
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

def get_user(request):
    """
    Parses the 'bearer' value of the HTTP Authorization header.
    @return: the `user` object if successfully authenticated by JWT
    """
    user = None
    jwtpayload = get_dict(request)
    if jwtpayload:
        username = jwtpayload.get('user', None)
        if username:
            try:
                user = get_user_model().objects.get(username=username)
            except get_user_model().DoesNotExist:
                log.error('JWT user, name: %s, error: does not exist', username)
    return user

def get_token_exp(token):
    claims = jwt.get_unverified_claims(token)
    return int(claims.get('exp'))

def generate(user):
    """ Generates the new JWT for given user """
    return jwt.encode(
        {
            'user': user.username,
            'exp': int(time.time()) + settings.AUTH_JWT_EXPIRE_AFTER_SEC,
        },
        settings.SECRET_KEY, algorithm=settings.AUTH_JWT_ALGORITHM
    )
