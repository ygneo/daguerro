from photologue.models import Photo
from daguerro.models import Tag


def run(*args):
    print "Creating tags... "
    for photo in Photo.objects.all():
        tags = photo.tags.split(" ")
        for tag in tags:
            t, _ = Tag.objects.get_or_create(name=tag)
    print "DONE"
