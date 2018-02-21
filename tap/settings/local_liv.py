from .base import *  # noqa

ALLOWED_HOSTS = ['tap.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_tap_liv',
        'USER': 'app_tap',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''
