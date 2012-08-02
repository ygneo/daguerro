import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import curry
from utils import safe_custom_field_name

FIELD_TYPE_CHOICES = (
    ('CharField', _('CharField')),
    ('IntegerField', _('IntegerField')),
    ('FloatField', _('FloatField')),
    ('URLField', _('URLField')),
    )


class CustomFieldsMixin(models.Model):

    class Meta:
        abstract = True

    def _get_FIELD(self, name):
        return self.custom_fields.get_value(name)

    def __init__(self, *args, **kwargs):
        super(CustomFieldsMixin, self).__init__(*args, **kwargs)
        self.add_custom_fields_to_attrs()

    def save(self, *args, **kwargs):
        self.add_custom_fields_to_attrs()
        super(CustomFieldsMixin, self).save(*args, **kwargs)

    def add_custom_fields_to_attrs(self):
        ctype = ContentType.objects.get_for_model(self)
        for custom_field in CustomField.objects.filter(content_type=ctype):
            field_name = safe_custom_field_name(custom_field.name)
            setattr(self, '%s' % field_name, self._get_FIELD(custom_field.name))


class CustomField(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    field_type = models.CharField(_('Field type'), max_length=15, choices=FIELD_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType)
    required = models.BooleanField(_('Required'), default=False)


    def __unicode__(self):
        return self.name

    def clean(self):
        Class = self.content_type.model_class()
        if self.name in [f.name for f in Class._meta.fields]:
            raise ValidationError("Content type %s already has a field named %s" %
                                  (self.content_type, self.name))



class GenericCustomFieldManager(models.Manager):

    def get_value(self, name):
        try:
            return self.get(field__name=name).value
        except GenericCustomField.DoesNotExist:
            return None


class GenericCustomField(models.Model):
    field = models.ForeignKey(CustomField)
    value = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = GenericCustomFieldManager()
    
    class Meta:
        unique_together = ('field', 'content_type', 'object_id')

    def __unicode__(self):
        return u"%s" % self.field

    @property
    def name(self):
        return self.field.name
    
    def clean(self):
        if self.field.content_type != self.content_type:
            raise ValidationError("Not a valid custom field for content type %s" %
                                  self.content_type)
            
        
    
