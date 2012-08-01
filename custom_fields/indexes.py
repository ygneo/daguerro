from haystack import indexes
from utils import safe_custom_field_name
from models import CustomField


class CustomFieldsIndexBase(indexes.DeclarativeMetaclass):

    def __new__(cls, name, bases, attrs):
        for cf in CustomField.objects.all():
            field_name = safe_custom_field_name(cf.name)
            attrs.update({field_name: indexes.CharField(
                        null=True,
                        model_attr="%s" % field_name)})
        return super(CustomFieldsIndexBase, cls).__new__(cls, name, bases, attrs)


class CustomFieldsIndex(indexes.RealTimeSearchIndex):
    __metaclass__ = CustomFieldsIndexBase
