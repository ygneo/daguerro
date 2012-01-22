from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def redirect_to_gallery(slugs=None):
    return HttpResponseRedirect(reverse('daguerro-gallery', kwargs={'slugs':slugs} if slugs else {}))
