import datetime
from django.db.models import Q
from haystack import indexes
from photologue.models import Photo, PhotoQuerySet
from custom_fields.indexes import CustomFieldsIndex
from haystack.query import SearchQuerySet


class PhotoIndex(CustomFieldsIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')
    caption = indexes.CharField(model_attr='caption', null=True)
    location_title = indexes.CharField(model_attr='location_title', null=True)
    tags = indexes.CharField(null=True)
    galleries_ids = indexes.MultiValueField(null=True)

    def get_model(self):
        return Photo

    def index_queryset(self):
        return Photo.objects.exclude_gallery_thumbs()

    def prepare_galleries_ids(self, obj):
        return [g.id for g in obj.galleries.all()]

    def prepare_tags(self, obj):
        return ",".join([tag for tag in obj.tags.split(" ")])


class PhotoSearchQuerySet(SearchQuerySet, PhotoQuerySet):
    pass

PublicPhotosSearchQuerySet = PhotoSearchQuerySet().public()


