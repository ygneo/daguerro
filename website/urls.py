import os
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.views.generic.simple import direct_to_template

# Generic views
urlpatterns = patterns('website.views',
                       url(r'^$', 'gallery', {'slugs': None}, name='website-gallery'),
                       url(r'^buscar/$', 'search_photos', name='website-search-photos'),
                       url(r'^solicitar-fotos/$', 'send_request_photos', name='website-send-request-photos'),
                       url(r'(?P<gallery_slugs>.+)/foto/(?P<photo_slug>.+)$', 'photo', name='website-photo'),
                       url(r'(?P<slugs>.+)$', 'gallery', name='website-gallery'),
)

if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   ) + urlpatterns
