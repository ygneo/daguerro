import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from utils import get_class

FIELD_TYPE_CHOICES = (
    ('CF', 'CharField'),
    ('TF', 'TextField'),
    ('TF', 'IntegerField'),
    ('FF', 'FloatField'),
    ('UF', 'URLField'),
    )


class CustomField(models.Model):
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=5, choices=FIELD_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType)

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
                                      
    
