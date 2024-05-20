# Django settings for tobaccocessation project.
import os.path
from ctlsettings.shared import common

project = 'tobaccocessation'
base = os.path.dirname(__file__)
locals().update(common(project=project, base=base))

ACCOUNT_ACTIVATION_DAYS = 2

PROJECT_APPS = [
    'tobaccocessation.main',
    'tobaccocessation.activity_prescription_writing',
    'tobaccocessation.activity_virtual_patient',
]

MIDDLEWARE += [  # noqa
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'bootstrapform',
    'django_extensions',
    'pagetree',
    'pageblocks',
    'tobaccocessation.main',
    'tobaccocessation.activity_prescription_writing',
    'tobaccocessation.activity_virtual_patient',
    'quizblock',
    'registration',
    'markdownify.apps.MarkdownifyConfig',
]

# Pageblocks/Pagetree settings
PAGEBLOCKS = [
    'pageblocks.HTMLBlockWYSIWYG',
    'pageblocks.HTMLBlock',
    'quizblock.Quiz',
    'activity_prescription_writing.Block',
    'activity_virtual_patient.PatientAssessmentBlock',
]

LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 3600

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(base, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'stagingcontext.staging_processor',
                'gacontext.ga_processor',
                'tobaccocessation.main.views.context_processor'
            ],
        },
    },
]
