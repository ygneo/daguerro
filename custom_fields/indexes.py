from haystack import indexes
from models import CustomField


class CustomFieldsIndexBase(indexes.DeclarativeMetaclass):

    def __new__(cls, name, bases, attrs):
        for cf in CustomField.objects.all():
            attrs.update({cf.name: indexes.CharField(
                        null=True,
                        model_attr="%s" % cf.name)})
        return super(CustomFieldsIndexBase, cls).__new__(cls, name, bases, attrs)


class CustomFieldsIndex(indexes.Indexable):
    __metaclass__ = CustomFieldsIndexBase
