from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/tobaccocessation/tobaccocessation/templates",
)

MEDIA_ROOT="/var/www/tobaccocessation/uploads/"
# put any static media here to override app served static media
STATICMEDIA_MOUNTS = (
    ('/sitemedia', '/var/www/tobaccocessation/tobaccocessation/sitemedia'),	
)


DEBUG = False
TEMPLATE_DEBUG = DEBUG
