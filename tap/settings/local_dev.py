from .base import *  # noqa

ALLOWED_HOSTS = ['127.0.0.1',
                 'localhost'
                 '[::1]',
                 'tap-dev.kdl.kcl.ac.uk']

CACHE_REDIS_DATABASE = '2'
CACHES['default']['LOCATION'] = '127.0.0.1:6379:' + CACHE_REDIS_DATABASE

DEBUG = True

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_tap_dev',
        'USER': 'app_tap',
        'PASSWORD': '',
        'HOST': ''
    },
}

LOGGING_LEVEL = logging.DEBUG

LOGGING['loggers']['tap']['level'] = LOGGING_LEVEL

SECRET_KEY = ''

MONGO_DB_NAME = PROJECT_NAME + '_dev'

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar', ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass
