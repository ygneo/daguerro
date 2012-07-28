from models import CustomField, GenericCustomField
from django import forms
from utils import normalize_unicode
from form_utils.forms import BetterModelForm


class CustomFieldsMixin:

    def __init__(self, *args, **kwargs):
        self.custom_fields = self._get_custom_fields()
        self.custom_form_fields = self._get_custom_form_fields()
        self.fields.update(self.custom_form_fields)
        if self.fieldsets:
            self._add_custom_fields_to_fieldset()

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
            fs_fields = self.fieldsets.fieldsets[i][1]
            add_cfields = fs_fields.get('add_custom_fields',
                                        False)
            if add_cfields:
                fs_fields['fields'].extend(
                    self.custom_form_fields.keys())


class CustomFieldsModelForm(BetterModelForm,
                            CustomFieldsMixin):

    def __init__(self, *args, **kwargs):
        BetterModelForm.__init__(
            self, *args, **kwargs)
        CustomFieldsMixin.__init__(self)

        if self.instance:
            self._add_custom_fields_initial_values()

    def _add_custom_fields_initial_values(self):
        for custom_field in self.custom_fields:
            field_name = normalize_unicode(
                custom_field.name)
            value = self.instance.custom_fields.get_value(
                field_name)
            self.initial[field_name] = value

    def save(self, *args, **kwargs):
        model = super(CustomFieldsModelForm, self).save(
            *args, **kwargs)
        for custom_field in self.custom_fields:
            field_name = normalize_unicode(
                custom_field.name)
            obj, _ = model.custom_fields.get_or_create(
                field__name=custom_field.name,
                field=custom_field,
                content_type=custom_field.content_type,
                object_id=model.pk,
                )
            obj.value = self.cleaned_data[field_name]
            obj.save()
        return model
