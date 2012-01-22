from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from photologue.models import Gallery

def current_site(request):
    return {'current_site': Site.objects.get_current()}


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

