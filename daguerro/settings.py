from django import forms
from django.db.utils import DatabaseError
from django.conf import settings
from django.utils.translation import ugettext as _
import django_settings


def overwrite_required_apps_settings():
    try:
        dag_results_per_page = django_settings.get('DAG_RESULTS_PER_PAGE', default=20)
        settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE = dag_results_per_page
    except DatabaseError:
        pass

overwrite_required_apps_settings()


FIELD_CLASS = {'integer': 'IntegerField',
               'positive integer': 'BooleanField',
               'email': 'EmailField',
               'string': 'CharField',
               }
class SettingsForm(forms.Form):    
        
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields = {}
        for field_name in self.settings_fields:
            setting = django_settings.models.Setting.objects.get(name=field_name)
            FieldClass = getattr(forms, FIELD_CLASS[str(setting.setting_type)])
            self.fields.update({setting.name: 
                                FieldClass(label=_(setting.name),
                                           required=False,
                                           initial=setting.setting_object.value,
                                           )})


class BasicSettingsForm(SettingsForm):
    settings_fields = ['DAG_ALLOW_PHOTOS_IN_ROOT_GALLERY', 'DAG_RESULTS_PER_PAGE',]

    class Meta:
        model = django_settings.models.Setting
        row_attrs = {'DAG_ALLOW_PHOTOS_IN_ROOT_GALLERY': {'class': 'inline'},
                     }


class MailingSettingsForm(SettingsForm):
    settings_fields = ['DAG_SALES_EMAIL', 'DAG_SMTP_HOST', 'DAG_SMTP_HOST_USER',
                       'DAG_SMTP_PASSWORD', 'DAG_CONFIRMATION_MAIL_SUBJECT',]

    class Meta:
        model = django_settings.models.Setting
