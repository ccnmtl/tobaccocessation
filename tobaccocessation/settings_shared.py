# Django settings for tobaccocessation project.
import os.path
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    ".ccnmtl.columbia.edu",
    "localhost"]

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

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
        }
    }


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=main,activity_prescription_writing,'
    'activity_treatment_choice,activity_virtual_patient',
]

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_URL = '/uploads/'
ADMIN_MEDIA_PREFIX = '/media/'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    # 'tobaccocessation.main.middleware.ConsoleExceptionMiddleware'
)

ROOT_URLCONF = 'tobaccocessation.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Put application templates before these fallback ones:
    "/var/www/tobaccocessation/templates/",
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'staticmedia',
    'sorl.thumbnail',
    'django.contrib.admin',
    'smartif',
    'template_utils',
    'typogrify',
    'tinymce',
    'pagetree',
    'pageblocks',
    'main',
    'activity_treatment_choice',
    'activity_prescription_writing',
    'activity_virtual_patient',
    'quizblock',
    'deploy_specific',
    'django_nose',
]

if 'test' in sys.argv:
    # this should not be required for tests
    INSTALLED_APPS.remove('deploy_specific')

THUMBNAIL_SUBDIR = "thumbs"

# Pageblocks/Pagetree settings
PAGEBLOCKS = ['pageblocks.HTMLBlockWYSIWYG',
              'pageblocks.HTMLBlock',
              'pageblocks.ImageBlock',
              'quizblock.Quiz',
              'activity_treatment_choice.Block',
              'activity_prescription_writing.Block',
              'main.FlashVideoBlock']

LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'

# TinyMCE settings

TINYMCE_JS_URL = '/site_media/js/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = 'media/js/tiny_mce'

# if you set this to True, you may have to
# override TINYMCE_JS_ROOT with the full path on production
TINYMCE_COMPRESSOR = False
TINYMCE_SPELLCHECKER = True

TINYMCE_DEFAULT_CONFIG = {'cols': 80,
                          'rows': 30,
                          'plugins': 'table,spellchecker,paste,searchreplace',
                          'theme': 'simple',
                          }

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 900

AUTH_PROFILE_MODULE = 'main.UserProfile'

# if you add a 'deploy_specific' directory
# then you can put a settings.py file and templates/ overrides there
try:
    from deploy_specific.settings import *
    if 'EXTRA_INSTALLED_APPS' in locals():
        INSTALLED_APPS = EXTRA_INSTALLED_APPS + INSTALLED_APPS
except ImportError:
    pass

MANAGERS = ADMINS
