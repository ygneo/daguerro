import datetime
from haystack.indexes import *
from haystack import site
from photologue.models import Photo, Gallery
from django.db.models import Q


class PhotoIndex(RealTimeSearchIndex):
    text = CharField(document=True, model_attr='title')
    alternative_title = CharField(model_attr='alternative_title', null=True)
    caption = CharField(model_attr='caption', null=True)
    location_title = CharField(model_attr='location_title', null=True)
    family = CharField(model_attr='family', null=True)
    galleries = MultiValueField(null=True)

    def index_queryset(self):
        return Photo.objects.public().filter(~Q(galleries=None))

    def prepare_galleries(self, obj):
        return [g.id for g in obj.galleries.all()]

site.register(Photo, PhotoIndex)
