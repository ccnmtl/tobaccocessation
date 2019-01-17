# flake8: noqa
from tobaccocessation.settings_shared import *

try:
    from tobaccocessation.local_settings import *
except ImportError:
    pass


