from models import CustomField
from django import forms
from utils import safe_custom_field_name
from form_utils.forms import BetterModelForm


class CustomFieldsMixin:

    def __init__(self, 
                 model_name=None,
                 FieldClass=None,
                 filter_qs=None, 
                 initial={}):
        self.custom_fields = self._get_custom_fields(model_name, filter_qs)
        self.custom_form_fields = self._get_custom_form_fields(
            FieldClass, initial)
        self.fields.update(self.custom_form_fields)
        if self.fieldsets:
            self._add_custom_fields_to_fieldset()

    def _get_custom_form_fields(self, FieldClass=None, initial={}):
        custom_fields = {}
        for key, cf in self.custom_fields.iteritems():
            if not FieldClass:
                field_class_name = cf.field_type
                FieldClass = getattr(forms, field_class_name)            
            field = FieldClass(label=cf.verbose_name, required=cf.required,
                               initial=initial.get(key, None))
            custom_fields[key] = field
        return custom_fields

    def _get_custom_fields(self, model_name=None, filter_qs=None):
        if not model_name:
            model_name = self._meta.model.__name__
        cfields_objects = CustomField.objects.filter(
            content_type__model=model_name) 
        if filter_qs:
            cfields_objects = cfields_objects.filter_qs()
        custom_fields = {}
        for cfield in cfields_objects:
            field_name = safe_custom_field_name(cfield.name).lower()
            custom_fields[field_name] = cfield
        return custom_fields

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
        BetterModelForm.__init__(self, *args, **kwargs)
        CustomFieldsMixin.__init__(self)

        if self.instance:
            self._add_custom_fields_initial_values()

    def _add_custom_fields_initial_values(self):
        for key, custom_field in self.custom_fields.iteritems():
            value = self.instance.custom_fields.get_value(custom_field.name)
            self.initial[key] = value

    def save(self, *args, **kwargs):
        model = super(CustomFieldsModelForm, self).save(
            *args, **kwargs)
        for key, custom_field in self.custom_fields.iteritems():
            obj, _ = model.custom_fields.get_or_create(
                field__name=custom_field.name,
                field=custom_field,
                content_type=custom_field.content_type,
                object_id=model.pk,
                )
            obj.value = self.cleaned_data[key]
            obj.save()
        return model
