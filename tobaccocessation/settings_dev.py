# flake8: noqa
from tobaccocessation.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tobaccocessation',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
    }
}

COMPRESS_ROOT = "/var/www/tobaccocessation/tobaccocessation/media/"

DEBUG = False

try:
    from tobaccocessation.local_settings import *
except ImportError:
    pass
