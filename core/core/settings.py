import os
import sys
from datetime import timedelta
from pathlib import Path
from loguru import logger
from core.loguru_handler import InterceptHandler
import socket

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=s99!jrahn_)iiv+5n(-gv5l3*3hi^)m37@60@60ib^um3!d*i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'debug_toolbar',
    'drf_spectacular',

    'user_profile.apps.UserProfileConfig',
    'jwt_registration.apps.JwtRegistrationConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'user_profile.User'

STATIC_URL = "static/"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {

    'ROTATE_REFRESH_TOKENS': True,

    'BLACKLIST_AFTER_ROTATION': True,

    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),

    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),

}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "db": "1",
        },
    }
}
CELERY_BROKER_URL = 'redis://redis:6379/0'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'intercept': {
            '()': InterceptHandler,
            'level': 0,
        },
    },
    'loggers': {
        '': {
            'handlers': ['intercept'],
            'level': "ERROR",
            'propagate': True,
        },
    }
}

logger.remove()
logger.add(sys.stdout, level="DEBUG", backtrace=True)
logger.add("logs/debug.log", level="DEBUG", rotation="30 MB", backtrace=True, retention="1 days")
logger.add("logs/info.log", level="DEBUG", rotation="30 MB", backtrace=True, retention="3 days")
logger.add("logs/error.log", level="ERROR", rotation="30 MB", backtrace=True, retention="7 days")

SPECTACULAR_SETTINGS = {
    'TITLE': 'API Schema',
    'DESCRIPTION': 'Guide for the REST API',
    'VERSION': '1.0.0',
}

INTERNAL_IPS = [
    "127.0.0.1",
]

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

CACHE_LIVE_TIME = 60 * 60
USER_PROFILE_CACHE_KEY = 'user_profile_{user}'
STORAGE_ACCESS_KEY = os.environ.get('ACCESS_STORAGE_KEY')
STORAGE_SECRET_KEY = os.environ.get('SECRET_STORAGE_KEY')
BUCKET_NAME = 'bucket-for-user-avatar'
STORAGE_URL = f'https://s3.storage.selcloud.ru/'
