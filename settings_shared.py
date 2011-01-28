# Django settings for tobaccocessation project.
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'postgresql_psycopg2' # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'tobaccocessation' # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

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
    #'tobaccocessation.main.middleware.ConsoleExceptionMiddleware'
)

ROOT_URLCONF = 'tobaccocessation.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Put application templates before these fallback ones:
    "/var/www/tobaccocessation/templates/",
    os.path.join(os.path.dirname(__file__),"templates"),
)

INSTALLED_APPS = (
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
)

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
                          'plugins':'table,spellchecker,paste,searchreplace',
                          'theme' : 'simple',
                          }

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 900

AUTH_PROFILE_MODULE = 'main.UserProfile'

#if you add a 'deploy_specific' directory                                                                                                             
#then you can put a settings.py file and templates/ overrides there                                                                                   
try:
    from deploy_specific.settings import *
    if locals().has_key('EXTRA_INSTALLED_APPS'):
        INSTALLED_APPS = EXTRA_INSTALLED_APPS + INSTALLED_APPS
except ImportError:
    import sys
    print >> sys.stderr, '***** Importing deploy_specific.settings failed'
    sys.stderr.flush()
    pass

MANAGERS = ADMINS
