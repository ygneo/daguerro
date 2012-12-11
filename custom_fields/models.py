from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from utils import safe_custom_field_name


FIELD_TYPE_CHOICES = (
    ('CharField', _('CharField')),
    ('IntegerField', _('IntegerField')),
    ('FloatField', _('FloatField')),
    ('URLField', _('URLField')),
    )


class CustomField(models.Model):
    name = models.CharField(_('Field name'), max_length=50, blank=True)
    verbose_name = models.CharField(_('Verbose name'), max_length=50)
    field_type = models.CharField(_('Field type'), max_length=15, choices=FIELD_TYPE_CHOICES)
    content_type = models.ForeignKey(ContentType)
    required = models.BooleanField(_('Required'), default=False)

    def __unicode__(self):
        return self.verbose_name

    def save(self, *args, **kwargs):
        self.name = "cf_" + safe_custom_field_name(self.verbose_name)
        super(CustomField, self).save(*args, **kwargs)

    def clean(self):
        Class = self.content_type.model_class()
        if self.name in [f.name for f in Class._meta.fields]:
            raise ValidationError("Content type %s already has a field named %s" %
                                  (self.content_type, self.name))


class CustomFieldsMixin(models.Model):

    class Meta:
        abstract = True

    def __getattr__(cls, key):
        if key and key.startswith("cf_"):
            return cls.custom_fields.get_value(key)
        else:
            raise AttributeError("Object using CustomFieldsMixin has no attribute '%s'" % key)


class CustomFieldQuerySet(models.query.QuerySet):
    
    def order_by_custom_fields(self, *fields):
        qs = self
        cfs_dict = dict(CustomField.objects.all().values_list("name", "id"))
        custom_fields = [field for field in fields 
                         if field and field.replace("-", "").startswith("cf_")]
        core_fields = tuple(set(fields) - set(custom_fields))
        if len(custom_fields) == 0:
            qs = qs.order_by(*core_fields)
        if len(custom_fields) == 1:
            field = custom_fields[0]
            field_id = cfs_dict[field.replace("-", "")]
            qs = qs.extra(select={"value": 
                                  """SELECT value 
                                         FROM custom_fields_genericcustomfield 
                                         WHERE field_id=%s AND object_id=photologue_photo.id"""},
                          select_params=(field_id,))
            direction = "-" if field.startswith("-") else ""
            qs = qs.order_by(*("%svalue" % direction,) + core_fields)
        elif len(custom_fields) > 1:
            raise Exception("No multiple custom fields are allowed in ordering")
        return qs


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
            
        
    
