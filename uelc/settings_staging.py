# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/uelc/uelc/uelc/templates",
)

MEDIA_ROOT = '/var/www/uelc/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/media', '/var/www/uelc/uelc/media'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'uelc_stage',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/uelc/uelc/media/"
DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

STATSD_PREFIX = 'uelc-staging'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass
