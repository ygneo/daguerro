from haystack import indexes
from photologue.models import Photo, PhotoQuerySet
from custom_fields.indexes import CustomFieldsIndex
from haystack.query import SearchQuerySet


class PhotoIndex(CustomFieldsIndex, indexes.Indexable, indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, model_attr='title')
    caption = indexes.CharField(model_attr='caption', null=True)
    location_title = indexes.CharField(model_attr='location_title', null=True)
    tags = indexes.CharField(null=True)
    is_public = indexes.BooleanField(model_attr='is_public')
    galleries_ids = indexes.MultiValueField(null=True)

    def get_model(self):
        return Photo

    def index_queryset(self):
        return Photo.objects.exclude_gallery_thumbs()

    def prepare_galleries_ids(self, obj):
        return [g.id for g in obj.galleries.all()]

    def prepare_tags(self, obj):
        return ",".join([tag for tag in obj.tags.split(" ")])

    def prepare_is_public(self, obj):
        return '' if not obj.is_public else 'True'

class PhotoSearchQuerySet(SearchQuerySet, PhotoQuerySet):
    pass

PublicPhotosSearchQuerySet = PhotoSearchQuerySet().public()


