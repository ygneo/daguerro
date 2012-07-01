from mptt.models import MPTTModelBase
from django.core.management.base import BaseCommand, CommandError
from photologue.models import Photo


class Command(BaseCommand):
    help = ('Add gallery parents titles to photo tags')

    requires_model_validation = True

    def handle(self, *args, **options):
        for photo in Photo.objects.all():
            for gallery in photo.galleries.all():
                title = gallery.title.lower()
                if title not in photo.tags:
                    photo.tags = photo.tags + " " + title
                photo.save()

