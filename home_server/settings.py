"""
Django settings for home_server project.
"""

import os
from pathlib import Path
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-hlla1ts_=lorr8o77^$jz+q5gqf=8qy5f(@m&ws#z&hjyb=7q-'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'appliances',
    'control',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'home_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'accounts' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'home_server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'home_server/static'),
    os.path.join(BASE_DIR, 'appliances/static'),
    os.path.join(BASE_DIR, 'static'),  # Add this if you have a global static folder
]

# Add this for modern JavaScript
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


# This is the base URL where media files will be accessed in the browser
MEDIA_URL = '/media/'

# This is the folder where uploaded files will be stored (outside the app)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Authentication settings
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/appliances/devices/'
LOGOUT_REDIRECT_URL = '/accounts/login/'


SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = TrueX_FRAME_OPTIONS = 'DENY'


# MQTT Configuration (if using MQTT)
MQTT_BROKER_HOST = '192.168.0.59'
MQTT_BROKER_PORT = 1883
# Optionally add:
# MQTT_USERNAME = 'your_username'
# MQTT_PASSWORD = 'your_password'

# For compatibility with code expecting MQTT_BROKER and MQTT_PORT
MQTT_BROKER = MQTT_BROKER_HOST
MQTT_PORT = MQTT_BROKER_PORT

# ESPHome Discovery Settings
ESPHOME_DISCOVERY = {
    'NETWORK_RANGE': '192.168.0.59/60',  # Your network range
    'SCAN_TIMEOUT': 5,  # Seconds to wait for device response
    'AUTO_DISCOVERY_INTERVAL': 300,  # Seconds between auto-discovery runs
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'control': {  # Replace with your app name
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}