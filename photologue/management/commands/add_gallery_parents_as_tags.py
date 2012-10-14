from django.core.management.base import BaseCommand
from photologue.models import Photo


class Command(BaseCommand):
    help = ('Add gallery parents titles to photo tags')

    requires_model_validation = True

    def handle(self, *args, **options):
        count = 0 
        for photo in Photo.objects.all():
            photo_tags_changed = False
            count += 1
            for gallery in photo.galleries.all():
                title = gallery.title.lower()
                if title not in photo.tags:
                    photo_tags_changed = True
                    photo.tags = photo.tags + " " + title
            if photo_tags_changed:
                photo.save()
        print "Procesed", count, "photos."

