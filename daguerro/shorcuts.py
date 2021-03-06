from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


def redirect_to_gallery(slugs, gallery=None, action=None, page=None):
    if action == "edit":
        slugs = _rebuild_slugs(slugs, gallery)
    url = reverse('daguerro-gallery', kwargs={'slugs':slugs} if slugs else {})
    if page:
        url += "?page=" + page
    return HttpResponseRedirect(url)


def _rebuild_slugs(slugs, gallery):
    slug_list = slugs.split("/")
    if len(slug_list) >= 1:
        slugs = "/".join(slug_list[:-1] + [gallery.title_slug])
    return slugs
    
