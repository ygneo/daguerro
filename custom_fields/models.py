import json
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from utils import get_class

FIELD_TYPE_CHOICES = (
    ('CF', 'CharField'),
    ('FF', 'FloatField'),
    ('UF', 'URLField'),
    ('LF', 'LinkField'),
    )


class Link():

    def __init__(self, value):
        value_dict = json.loads(value)
        self.title, self.url = (value_dict['title'], value_dict['url'])
        

class CustomField(models.Model):
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=5, choices=FIELD_TYPE_CHOICES)

    def __unicode__(self):
        return self.name


class GenericCustomField(models.Model):
    field = models.ForeignKey(CustomField)
    raw_value = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return u"%s" % self.field

    @property
    def name(self):
        return self.field.name
    
    @property
    def value(self):
        if self.field.field_type == "LF":
            return Link(self.raw_value)
        else:
            return self.raw_value

    def clean(self):        
        field_type = self.field.get_field_type_display()
        if self.field.field_type == "LF":
            try:
                json.loads(self.raw_value)
            except:
                raise ValidationError('JSON value of %s %s is invalid' % 
                                      (field_type, self.name,)
                                      )
        else:
            FieldClass = get_class("django.db.models.%s" % field_type)
            FieldClass().clean(self.value, self)
        
                                      
    

    
