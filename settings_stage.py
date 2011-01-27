from settings_shared import *

TEMPLATE_DIRS = (
    "/usr/local/share/sandboxes/common/tobaccocessation/tobaccocessation/templates",
)

MEDIA_ROOT="/usr/local/share/sandboxes/common/tobaccocessation/uploads/"

DEBUG = False
TEMPLATE_DEBUG = DEBUG

import sys
print >> sys.stderr, 'MEDIA_ROOT %s' % MEDIA_ROOT
sys.stderr.flush()
