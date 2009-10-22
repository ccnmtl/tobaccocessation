from settings_shared import *

DATABASE_ENGINE = 'postgresql_psycopg2'

TEMPLATE_DIRS = (
    "/usr/local/share/sandboxes/common/tobaccocessation/tobaccocessation/templates",
)

MEDIA_ROOT = '/usr/local/share/sandboxes/common/tobaccocessation/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
