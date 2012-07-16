from models import CustomField
from django import forms


class CustomFieldsMixin(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CustomFieldsMixin , self).__init__(*args, **kwargs)
        
        custom_fields = {}
        model_name = self._meta.model.__name__
        for cf in CustomField.objects.filter(content_type__model=model_name):
            FieldClass = getattr(forms,  cf.get_field_type_display())
            custom_fields[cf.name] = FieldClass()
        self.fields.update(custom_fields)

        return self
