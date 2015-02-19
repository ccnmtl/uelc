# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

MEDIA_ROOT = '/var/www/uelc/uploads/'
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/media', '/var/www/uelc/uelc/media'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'uelc',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
    }
}

AWS_STORAGE_BUCKET_NAME = "ccnmtl-uelc-static-stage"
AWS_PRELOAD_METADATA = True

STATICFILES_STORAGE = 'uelc.s3utils.MediaRootS3BotoStorage'
S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = 'https://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = 'uelc.s3utils.MediaRootS3BotoStorage'
MEDIA_URL = S3_URL + '/media/'
COMPRESS_STORAGE = 'uelc.s3utils.CompressorS3BotoStorage'

COMPRESS_ROOT = "/var/www/uelc/uelc/media/"
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
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
