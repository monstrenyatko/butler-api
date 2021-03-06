"""
Django settings.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import sys
import os.path
from datetime import timedelta
import logging


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Deployment checklist
#  https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# The secret key must be a large random value and it must be kept secret
SECRET_KEY = os.environ.get('BUTLER_API_DJANGO_SECRET_KEY')

# Disabled debug mode by default
DEBUG = bool(os.environ.get('DEBUG', False))

# Logger settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(process)d] [%(levelname)s] [%(module)s:%(lineno)d] '
                      '%(message)s'
        },
        'simple': {
            'format': '[%(asctime)s]  [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': os.environ.get('BUTLER_API_DJANGO_LOG_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.template': {
            'handlers': ['console'],
            'level': os.environ.get('BUTLER_API_DJANGO_TEMPLATE_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': os.environ.get('BUTLER_API_DJANGO_REQ_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': os.environ.get('BUTLER_API_DJANGO_DB_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'mqtt_manager.services.data_recorder.mqtt_client': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

ALLOWED_HOSTS = [os.environ.get('BUTLER_HOST', 'butler'), 'localhost', '127.0.0.1', '[::1]']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'session_security',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
    'auth_manager.apps.AuthManagerConfig',
    'fw_manager.apps.FwManagerConfig',
    'cert_manager.apps.CertManagerConfig',
    'mqtt_manager.apps.MqttManagerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'session_security.middleware.SessionSecurityMiddleware',
]

ROOT_URLCONF = 'butler_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'butler_api', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'butler_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('BUTLER_DB_NAME'),
        'USER': os.environ.get('BUTLER_DB_USER'),
        'PASSWORD': os.environ.get('BUTLER_DB_PASSWORD'),
        'HOST': os.environ.get('BUTLER_DB_HOST'),
        'PORT': os.environ.get('BUTLER_DB_PORT', ''),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'time-series': {
        'NAME': os.environ.get('BUTLER_TSDB_NAME'),
        'USER': os.environ.get('BUTLER_TSDB_USER'),
        'PASSWORD': os.environ.get('BUTLER_TSDB_PASSWORD'),
        'HOST': os.environ.get('BUTLER_TSDB_HOST'),
        'PORT': os.environ.get('BUTLER_TSDB_PORT'),
    },
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = []


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Django REST framework
# http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'PAGE_SIZE': 10,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.JSONParser',
    ],
}


# Django REST Swagger
# https://django-rest-swagger.readthedocs.io
SWAGGER_SETTINGS = {
    'is_authenticated': True,  # Enforce user authentication
    'is_superuser': False,  # Admin only access
    'USE_SESSION_AUTH': False,
    'VALIDATOR_URL': None,
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'API Key format: token <token-value>',
        }
    },
}

# Other settings

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SECURITY_WARN_AFTER = int(os.environ.get('BUTLER_SESSION_SECURITY_WARN_AFTER', 540))
SESSION_SECURITY_EXPIRE_AFTER = int(os.environ.get('BUTLER_SESSION_SECURITY_EXPIRE_AFTER', 600))
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 0
AUTH_TIME_INTERVAL = timedelta(minutes=15)
AUTH_JWT_EXPIRE_AFTER_SEC = int(os.environ.get('BUTLER_AUTH_JWT_EXPIRE_AFTER_SEC', 15*24*60*60))
AUTH_JWT_ALGORITHM = 'HS256'
MEDIA_ROOT = os.environ.get('BUTLER_MEDIA', os.path.join(os.environ.get('BUTLER_HOME'), 'media'))
MEDIA_URL = '/media/'
APP_DATA_CERT_ROOT = MEDIA_ROOT
APP_DATA_CERT_SUBDIR = 'cert'
APP_DATA_CERT_DIR = os.path.join(APP_DATA_CERT_ROOT, APP_DATA_CERT_SUBDIR)
APP_DATA_CERT_KEY_FILE_UID = int(os.environ.get('BUTLER_CERT_KEY_UID', -1))
APP_DATA_CERT_KEY_FILE_GID = int(os.environ.get('BUTLER_CERT_KEY_GID', -1))
APP_DATA_CERT_KEY_FILE_MODE = int(os.environ.get('BUTLER_CERT_KEY_MODE','660'), 8)
APP_DATA_FW_ROOT = MEDIA_ROOT
APP_DATA_FW_SUBDIR = 'fw'
APP_DATA_FW_UNUSED_DELAY = timedelta(minutes=5)


# Sensor measurements mapping
MEASUREMENTS = {
    'TEMPERATURE': 'TEMPERATURE',
    'TEMP': 'TEMPERATURE',
    'LIGHT': 'LIGHT',
    'HUMIDITY': 'HUMIDITY',
    'HUMID': 'HUMIDITY',
}


# Load external config if required
EXTERNAL_SETTINGS = os.environ.get('BUTLER_API_DJANGO_EXTERNAL_SETTINGS_DIR', None)
if EXTERNAL_SETTINGS:
    sys.path.append(os.path.abspath(EXTERNAL_SETTINGS))
    try:
        from external_settings import *
    except ImportError as e:
        logging.getLogger(__name__).warn("Can't load `external_settings.py` from {}, error: {}".format(EXTERNAL_SETTINGS, str(e)))
