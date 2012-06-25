import datetime
from haystack.indexes import *
from haystack import site
from photologue.models import Photo, Gallery
from django.db.models import Q


class PhotoIndex(RealTimeSearchIndex):
    text = CharField(document=True, model_attr='title', use_template=True,
                     template_name='photologue/search/photo_title.txt')
    alternative_title = CharField(model_attr='alternative_title', null=True)
    caption = CharField(model_attr='caption', null=True)
    location_title = CharField(model_attr='location_title', null=True)
    family = CharField(model_attr='family', null=True)
    tags = MultiValueField(null=True)
    galleries_ids = MultiValueField(null=True)
    galleries_titles = CharField(null=True)

    def index_queryset(self):
        return Photo.objects.public().filter(~Q(galleries=None))

    def prepare_galleries_ids(self, obj):
        return [g.id for g in obj.galleries.all()]

    def prepare_galleries_titles(self, obj):
        return ",".join([g.title for g in obj.galleries.all()])

    def prepare_tags(self, obj):
        return [tag for tag in obj.tags.split(" ")]

    def prepare_template(self, obj):
        print super(PhotoIndex, self).prepare_template(self, obj)
        return super(PhotoIndex, self).prepare_template(self, obj)

site.register(Photo, PhotoIndex)
