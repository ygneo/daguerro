from website.urls import urlpatterns
from photologue.models import Gallery, Photo

def header_info(request):
    extra_context = {}
    if 'daguerro' not in request.path:
        root_galleries = Gallery.objects.public().filter(parent=None)
        photo_count = Photo.objects.public().count()
        extra_context = {'galleries': root_galleries, 'photo_count': photo_count}
    return extra_context

