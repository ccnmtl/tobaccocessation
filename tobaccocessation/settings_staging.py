import sys
from django.conf import settings
from tobaccocessation.settings_shared import *  # noqa: F403
from ctlsettings.staging import common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


locals().update(
    common(
        project=project,  # noqa: F405
        base=base,  # noqa: F405
        STATIC_ROOT=STATIC_ROOT,  # noqa: F405
        INSTALLED_APPS=INSTALLED_APPS,  # noqa: F405
        s3prefix='ccnmtl'
    ))

try:
    from tobaccocessation.local_settings import *  # noqa: F403
except ImportError:
    pass

if ('migrate' not in sys.argv) and \
   ('collectstatic' not in sys.argv) and \
   hasattr(settings, 'SENTRY_DSN'):
    sentry_sdk.init(
        dsn=SENTRY_DSN,  # noqa: F405
        integrations=[DjangoIntegration()],
        debug=True,
    )
