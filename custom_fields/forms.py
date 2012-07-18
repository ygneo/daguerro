from models import CustomField
from django import forms


class CustomFieldsMixin(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CustomFieldsMixin , self).__init__(
            *args, **kwargs)
        
        custom_fields = self._get_custom_fields()
        self.fields.update(custom_fields)
        self.fieldsets.fieldsets.append(
            ('custom_fields', {'fields': 
                               custom_fields.keys(),
                               'legend': ''}
            )
        )
        return self

    def _get_custom_fields(self):
        custom_fields = {}
        model_name = self._meta.model.__name__
        cfs = CustomField.objects.filter(
            content_type__model=model_name)
        for cf in cfs:
            field_class_name = cf.get_field_type_display()
            FieldClass = getattr(forms, field_class_name)
            custom_fields[cf.name] = FieldClass(required=cf.required)
        return custom_fields

