import os, sys, site

# enable the virtualenv
site.addsitedir('/var/www/uelc/uelc/ve/lib/python2.7/site-packages')

# paths we might need to pick up the project's settings
sys.path.append('/var/www/uelc/uelc/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'uelc.settings_production'

import django
django.setup()
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
