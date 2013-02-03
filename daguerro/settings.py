from django import forms
from django.conf import settings
import django_settings


def overwrite_required_apps_settings():
    dag_results_per_page = django_settings.get('DAG_RESULTS_PER_PAGE', default=20)
    settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE = dag_results_per_page

overwrite_required_apps_settings()


FIELD_CLASS = {'integer': 'IntegerField',
               'positive integer': 'BooleanField',
               'email': 'EmailField',
               'string': 'CharField',
               }
class SettingsForm(forms.ModelForm):    
    class Meta:
        model = django_settings.models.Setting
        
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.fields = {}
        for field_name in self.settings_fields:
            setting = self._meta.model.objects.get(name=field_name)
            FieldClass = getattr(forms, FIELD_CLASS[str(setting.setting_type)])
            self.fields.update({setting.name: 
                                FieldClass(label=setting.name,
                                           required=False,
                                           initial=setting.setting_object.value)})


class BasicSettingsForm(SettingsForm):
    settings_fields = ['DAG_ALLOW_PHOTOS_IN_ROOT_GALLERY', 'DAG_RESULTS_PER_PAGE',]


class MailingSettingsForm(SettingsForm):
    settings_fields = ['DAG_SALES_EMAIL', 'DAG_SMTP_HOST', 'DAG_SMTP_HOST_USER',
                       'DAG_SMTP_PASSWORD', 'DAG_CONFIRMATION_MAIL_SUBJECT',]

