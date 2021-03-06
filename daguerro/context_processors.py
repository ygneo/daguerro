from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from photologue.models import Gallery
from daguerro.utils import daguerro_settings_to_dict

def current_site(request):
    try:
        current_site =  Site.objects.get_current()
    except:
        current_site = None
    return {'current_site': current_site}


def daguerro_settings(request):
    return {'daguerro_settings': daguerro_settings_to_dict}


def category_thread(request):
    slugs = request.META['PATH_INFO']
    parent_categories = []
    # First slugs are not relevant (should be 'daguerro/gallery/')
    list_slugs = slugs.split('/')[3:]
    if list_slugs and list_slugs[0]:
        i = 0
        for slug in list_slugs:
            i += 1
            category = get_object_or_404(Gallery, title_slug=slug)
            category.slugs_path = '/'.join(list_slugs[:i])
            parent_categories.append(category)

    # When no slugs passed, parent_categories is empty, and return
    # galleries with parent=None (first level)
    current_category = parent_categories[-1] if len(parent_categories) else None

    return {'parent_categories': parent_categories,
            'current_category': current_category}


def settings_processor(request):
    if 'daguerro' in request.path:
        settings_dict = {'default_photo_ordering_fields':
                             settings.DAG_DEFAULT_PHOTO_ORDERING_FIELDS}
        return {'settings': settings_dict}
    return {}
