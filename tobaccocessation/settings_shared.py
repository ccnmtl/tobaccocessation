# Django settings for tobaccocessation project.
import os.path
from ccnmtlsettings.shared import common

project = 'tobaccocessation'
base = os.path.dirname(__file__)
locals().update(common(project=project, base=base))

ACCOUNT_ACTIVATION_DAYS = 2

PROJECT_APPS = [
    'tobaccocessation.main',
    'tobaccocessation.activity_prescription_writing',
    'tobaccocessation.activity_virtual_patient',
]

USE_TZ = True

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'tobaccocessation.main.views.context_processor'
)

INSTALLED_APPS += [  # noqa
    'sorl.thumbnail',
    'typogrify',
    'bootstrapform',
    'django_extensions',
    'pagetree',
    'pageblocks',
    'tobaccocessation.main',
    'tobaccocessation.activity_prescription_writing',
    'tobaccocessation.activity_virtual_patient',
    'quizblock',
    'registration',
]

# Pageblocks/Pagetree settings
PAGEBLOCKS = [
    'pageblocks.HTMLBlockWYSIWYG',
    'pageblocks.HTMLBlock',
    'pageblocks.ImageBlock',
    'quizblock.Quiz',
    'activity_prescription_writing.Block',
    'activity_virtual_patient.PatientAssessmentBlock',
]

LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL = '/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_AGE = 3600
