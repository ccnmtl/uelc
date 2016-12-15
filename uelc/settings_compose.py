# flake8: noqa
from settings_shared import *

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

WINDSOCK_BROKER_URL = "tcp://broker:5555"
ZMQ_APPNAME = "uelc"
WINDSOCK_SECRET = "6f1d916c-7761-4874-8d5b-8f8f93d20bf2"

# browsers are strict about security around SSL certificates
# and need the host to match up with the certificate
#
# you will need to either make an /etc/hosts entry for windsock.ccnmtl
# pointing to your host, or you will need to make a local_settings.py
# that overrides this setting with the right hostname.
WINDSOCK_WEBSOCKETS_BASE = "ws://localhost:5050/socket/"

try:
    from local_settings import *
except ImportError:
    pass
