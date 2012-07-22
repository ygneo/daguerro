from models import CustomField, GenericCustomField
from django import forms
from utils import normalize_unicode

class CustomFieldsMixin(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(CustomFieldsMixin , self).__init__(
            *args, **kwargs)

        self.custom_fields = self._get_custom_fields()
        self.custom_form_fields = self._get_custom_form_fields()
        self.fields.update(self.custom_form_fields)
        if self.instance:
            self._add_custom_fields_initial_values()
        if self.fieldsets:
            self._add_custom_fields_to_fieldset()
        return self

    def _get_custom_form_fields(self):
        custom_fields = {}
        for cf in self.custom_fields:
            field_class_name = cf.field_type
            FieldClass = getattr(forms, field_class_name)
            field = FieldClass(label=cf.name, required=cf.required)
            custom_fields[normalize_unicode(cf.name)] = field
        return custom_fields

    def _get_custom_fields(self):
        model_name = self._meta.model.__name__
        return CustomField.objects.filter(
            content_type__model=model_name) 

    def _add_custom_fields_to_fieldset(self):
        for i in range(len(self.fieldsets.fieldsets)):
            fs = self.fieldsets.fieldsets[i]
            if fs[0] == "basic-metadata":
                fs[1]['fields'].extend(self.custom_form_fields.keys())

    def _add_custom_fields_initial_values(self):
        for custom_field in self.custom_fields:
            field_name = normalize_unicode(custom_field.name)
            value = self.instance.custom_fields.get_value(field_name)
            self.initial[field_name] = value

    def save(self, force_insert=False, force_update=False, commit=True):
        model = super(CustomFieldsMixin, self).save(commit=False)
        if commit:
            for custom_field in self.custom_fields:
                field_name = normalize_unicode(custom_field.name)
                obj, created = model.custom_fields.get_or_create(
                    field__name=custom_field.name,
                    field=custom_field,
                    content_type=custom_field.content_type,
                    object_id=self.instance.pk,
                    )
                obj.value = self.cleaned_data[field_name]
                obj.save()
        return model

    def custom_fields(self):
        for name in self.custom_form_fields():
            yield (self.fields[name].label, value)

