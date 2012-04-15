import os
import django
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
from haystack.views import SearchView

js_info_dict = {
    'packages': ('website',),
}
urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns = urlpatterns + patterns('website.views',
#                       url(r'^buscar/$', 'search_photos', name='website-search-photos'),
                       url(r'^buscar', SearchView(template='website/search_results.html'), 
                           name='website-search-photos'),
                       url(r'^solicitar-fotos/$', 'send_request_photos', 
                           name='website-send-request-photos'),
                       url(r'(?P<gallery_slugs>.+)/foto/(?P<photo_slug>.+)$', 'photo', 
                           name='website-photo'),
                       url(r'(?P<slugs>.+)$', 'gallery', name='website-gallery'),
                       url(r'^$', 'gallery', {'slugs': None}, name='website-gallery'),
)




if settings.DEBUG:
    urlpatterns = patterns('',
                           url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
                               {'document_root': settings.MEDIA_ROOT,}),
                           url(r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', 
                               {'document_root': os.path.join(django.__path__[0], 
                                                              "contrib/admin/media/")}),
   ) + urlpatterns
