from models import CustomField
from django import forms
from utils import normalize_unicode

class CustomFieldsMixin(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CustomFieldsMixin , self).__init__(
            *args, **kwargs)
        
        custom_fields = self._get_custom_fields()
        self.fields.update(custom_fields)
        for i in range(len(self.fieldsets.fieldsets)):
            fs = self.fieldsets.fieldsets[i]
            if fs[0] == "basic-metadata":
                fs[1]['fields'].extend(custom_fields.keys())
        return self

    def _get_custom_fields(self):
        custom_fields = {}
        model_name = self._meta.model.__name__
        cfs = CustomField.objects.filter(
            content_type__model=model_name)
        for cf in cfs:
            field_class_name = cf.field_type
            FieldClass = getattr(forms, field_class_name)
            field = FieldClass(label=cf.name, required=cf.required)
            custom_fields[normalize_unicode(cf.name)] = field
        return custom_fields

