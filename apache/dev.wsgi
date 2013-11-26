import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/tobaccocessation/tobaccocessation/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/tobaccocessation/tobaccocessation/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'tobaccocessation.settings_dev'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
