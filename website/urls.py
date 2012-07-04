import os
import django
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template
from website.views import SearchPhotosView
from django.views.generic.simple import redirect_to

js_info_dict = {
    'packages': ('website',),
}
urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns = urlpatterns + patterns('website.views',
                                     url(r'^buscar', SearchPhotosView(), 
                                         name='website-search-photos'),
                                     url(r'^solicitar-fotos/$', 'send_request_photos', 
                                         name='website-send-request-photos'),
                                     (r'^favicon.ico$', redirect_to, {'url':'/static/website/img/favicon.ico'}),
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
                           url(r'^wix', 'website.views.whoosh_search_index'),
   ) + urlpatterns
