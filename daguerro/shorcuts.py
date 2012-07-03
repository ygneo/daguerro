from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def redirect_to_gallery(slugs, gallery=None, action=None):
    if action == "edit":
        slugs = _rebuild_slugs(slugs, gallery)
    return HttpResponseRedirect(reverse('daguerro-gallery', kwargs={'slugs':slugs} if slugs else {}))


def _rebuild_slugs(slugs, gallery):
    slug_list = slugs.split("/")
    if len(slug_list) >= 1:
        slugs = "/".join(slug_list[:-1] + [gallery.title_slug])
    return slugs
    
