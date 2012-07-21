import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


FIELD_TYPE_CHOICES = (
    ('CharField', _('CharField')),
    ('TextField', _('TextField')),
    ('IntegerField', _('IntegerField')),
    ('FloatField', _('FloatField')),
    ('URLField', _('URLField')),
    )


class CustomField(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    field_type = models.CharField(_('Field type'), max_length=15, choices=FIELD_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType)
    required = models.BooleanField(_('Required'), default=False)
    searchable = models.BooleanField(_('Searchable'), default=False)

    def __unicode__(self):
        return self.name


class GenericCustomField(models.Model):
    field = models.ForeignKey(CustomField)
    value = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"%s" % self.field

    @property
    def name(self):
        return self.field.name

    
    def clean(self):
        if self.field.content_type != self.content_type:
            raise ValidationError("Not a valid custom field for content type %s" %
                                  self.content_type)
                                      
    
