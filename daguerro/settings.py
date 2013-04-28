from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.utils import DatabaseError
import django_settings
from django_settings.models import Setting
from django import forms


try:
    dag_results_per_page = django_settings.get('DAG_RESULTS_PER_PAGE', default=20)
    settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE = dag_results_per_page
except:
    pass


try:
    settings.EMAIL_HOST = django_settings.get('DAG_SMTP_HOST')
    settings.EMAIL_HOST_USER = str(django_settings.get('DAG_SMTP_HOST_USER'))
    settings.EMAIL_HOST_PASSWORD = str(django_settings.get('DAG_SMTP_PASSWORD'))
except:
    pass
