import os
import sys

sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'barres.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
sys.path.append('/home/ygneo/django_projects/barres-site')
sys.path.append('home/ygneo/django_projects/barres-site/barres')
