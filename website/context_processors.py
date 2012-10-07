from photologue.models import Gallery, Photo


def header_info(request):
    extra_context = {}
    if 'daguerro' not in request.path:
        root_galleries = Gallery.objects.filter(parent=None, is_public=True)
        photo_count = Photo.objects.exclude_gallery_thumbs().public().count()
        extra_context = {'galleries': root_galleries, 'photo_count': photo_count}
    return extra_context

