from django.conf import settings
import django_settings


try:
    dag_results_per_page = django_settings.get('DAG_RESULTS_PER_PAGE', default=20)
    settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE = dag_results_per_page
except:
    pass
