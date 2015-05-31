# Django settings for tobaccocessation project.
import os.path
import sys

ACCOUNT_ACTIVATION_DAYS = 2

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tobaccocessation',
        'HOST': '',
        'PORT': 5432,
        'USER': '',
        'PASSWORD': '',
        'ATOMIC_REQUESTS': True,
    }
}

if 'test' in sys.argv or 'jenkins' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'HOST': '',
            'PORT': '',
            'USER': '',
            'PASSWORD': '',
            'ATOMIC_REQUESTS': True,
        }
    }
DEBUG_TOOLBAR_PATCH_SETTINGS = False

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
)


PROJECT_APPS = ['tobaccocessation.main',
                'tobaccocessation.activity_prescription_writing',
                'tobaccocessation.activity_virtual_patient']

ALLOWED_HOSTS = [".ccnmtl.columbia.edu", "localhost"]

USE_TZ = True
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = False
MEDIA_ROOT = "/var/www/tobaccocessation/uploads"
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
STATIC_ROOT = ""
SECRET_KEY = ')ng#)ef_u@_^zvvu@dxm7ql-yb^_!a6%v3v^j3b(mp+)l+5%@h'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'stagingcontext.staging_processor',
    'djangowind.context.context_processor',
    'django.core.context_processors.static',
    'gacontext.ga_processor',
    'tobaccocessation.main.views.context_processor'
)


MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware'
)

ROOT_URLCONF = 'tobaccocessation.urls'

TEMPLATE_DIRS = (
    "/var/www/tobaccocessation/templates/",
    os.path.join(os.path.dirname(__file__), "templates"),
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'sorl.thumbnail',
    'tagging',
    'typogrify',
    'compressor',
    'django_statsd',
    'bootstrapform',
    'debug_toolbar',
    'waffle',
    'django_jenkins',
    'smoketest',
    'django_extensions',
    'impersonate',
    'tinymce',
    'smartif',
    'pagetree',
    'pageblocks',
    'tobaccocessation.main',
    'tobaccocessation.activity_prescription_writing',
    'tobaccocessation.activity_virtual_patient',
    'quizblock',
    'registration',
    'django_markwhat'
]

INTERNAL_IPS = ('127.0.0.1', )

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]


STATSD_CLIENT = 'statsd.client'
STATSD_PREFIX = 'tobaccocessation'
STATSD_HOST = '127.0.0.1'
STATSD_PORT = 8125

THUMBNAIL_SUBDIR = "thumbs"
EMAIL_SUBJECT_PREFIX = "[tobaccocessation] "
EMAIL_HOST = 'localhost'
SERVER_EMAIL = "tobaccocessation@ccnmtl.columbia.edu"
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', 'sitemedia'),
)

COMPRESS_URL = "/media/"
COMPRESS_ROOT = "media/"

# WIND settings
AUTHENTICATION_BACKENDS = ('djangowind.auth.SAMLAuthBackend',
                           'django.contrib.auth.backends.ModelBackend', )
CAS_BASE = "https://cas.columbia.edu/"
WIND_PROFILE_HANDLERS = ['djangowind.auth.CDAPProfileHandler']
WIND_AFFIL_HANDLERS = ['djangowind.auth.AffilGroupMapper',
                       'djangowind.auth.StaffMapper',
                       'djangowind.auth.SuperuserMapper']
WIND_STAFF_MAPPER_GROUPS = ['tlc.cunix.local:columbia.edu']
WIND_SUPERUSER_MAPPER_GROUPS = ['anp8', 'jb2410', 'zm4', 'egr2107',
                                'sld2131', 'amm8', 'mar227', 'jed2161',
                                'cld2156', 'njn2118']

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True
LOGIN_REDIRECT_URL = "/"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')

# Pageblocks/Pagetree settings
PAGEBLOCKS = ['pageblocks.HTMLBlockWYSIWYG',
              'pageblocks.HTMLBlock',
              'pageblocks.ImageBlock',
              'quizblock.Quiz',
              'activity_prescription_writing.Block',
              'activity_virtual_patient.PatientAssessmentBlock']

LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'

TINYMCE_SPELLCHECKER = True

TINYMCE_DEFAULT_CONFIG = {'cols': 80,
                          'rows': 30,
                          'plugins': 'table,spellchecker,paste,searchreplace',
                          'theme': 'simple'}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 3600

AUTH_PROFILE_MODULE = 'main.UserProfile'  # what is this for again?
# new django doc - AUTH_USER_MODEL = 'myapp.MyUser'
