# flake8: noqa
from settings_shared import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tobaccocessation',
        'HOST': '',
        'PORT': 6432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True

STATSD_PREFIX = 'tobaccocessation-staging'

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

# AWS Settings for staging
AWS_STORAGE_BUCKET_NAME = "ccnmtl-tobaccocessation-static-stage"
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
# static data, e.g. css, js, etc.
STATICFILES_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'
STATIC_URL = 'https://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'

# uploaded images
MEDIA_URL = 'https://%s.s3.amazonaws.com/uploads/' % AWS_STORAGE_BUCKET_NAME

try:
    from local_settings import *
except ImportError:
    pass
