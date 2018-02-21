from .base import *  # noqa

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
)

DEBUG = True

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'tap',
        'USER': 'tap',
        'PASSWORD': 'tap',
        'ADMINUSER': 'postgres',
        'HOST': 'localhost'
    },
}

# 10.0.2.2 is the default IP for the VirtualBox Host machine
INTERNAL_IPS = ['0.0.0.0', '127.0.0.1', '::1', '10.0.2.2']

SECRET_KEY = '12345'

FABRIC_USER = 'jvieira'

# -----------------------------------------------------------------------------
# Django Debug Toolbar
# http://django-debug-toolbar.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

try:
    import debug_toolbar  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ['debug_toolbar']
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware']
    DEBUG_TOOLBAR_PATCH_SETTINGS = True
except ImportError:
    pass

LOGGING['loggers']['tap'] = {}
LOGGING['loggers']['tap']['handlers'] = ['console']
LOGGING['loggers']['tap']['level'] = logging.DEBUG
LOGGING['loggers']['apscheduler'] = {}
LOGGING['loggers']['apscheduler']['handlers'] = ['console']
LOGGING['loggers']['apscheduler']['level'] = logging.DEBUG

TWITTER_API_KEY = '6z3jZEo51pbW7ZMlmQuoRZSvw'
TWITTER_API_SECRET = 'ec1Ty57LBwoaiOhVyOCayH4fFujrAjAKQgZ3MJVPe1qPY5LY17'
TWITTER_ACCESS_TOKEN = '15097059-PHJxWVmIvmmnxXqLNyZP3MiPdE4C9siu15BtCgtZp'
TWITTER_ACCESS_TOKEN_SECRET = 'wtnnrKQQ4tBuZ6HTNZmGw0LsSV4GWwy1LCgYo9a0kOY3D'
