import datetime
from haystack.indexes import *
from photologue.models import Photo
from django.db.models import Q


class PhotoIndex(RealTimeSearchIndex, Indexable):
    text = CharField(document=True, model_attr='title')
    alternative_title = CharField(model_attr='alternative_title', null=True)
    caption = CharField(model_attr='caption', null=True)
    location_title = CharField(model_attr='location_title', null=True)
    family = CharField(model_attr='family', null=True)
    tags = CharField(null=True)
    galleries_ids = MultiValueField(null=True)

    def get_model(self):
        return Photo

    def index_queryset(self):
        return Photo.objects.public().filter(~Q(galleries=None))

    def prepare_galleries_ids(self, obj):
        return [g.id for g in obj.galleries.all()]

    def prepare_tags(self, obj):
        return ",".join([tag for tag in obj.tags.split(" ")])

    def prepare_template(self, obj):
        print super(PhotoIndex, self).prepare_template(self, obj)
        return super(PhotoIndex, self).prepare_template(self, obj)
