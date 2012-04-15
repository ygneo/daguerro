from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('',
                       (r'^daguerro/', include('daguerro.urls')),
                       (r'^tinymce/', include('tinymce.urls')),
                       (r'', include('barres.website.urls')),
)


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

    from django.contrib import admin
    admin.autodiscover()
    urlpatterns = patterns('',
                           ('^admin/', include(admin.site.urls)),
                           (r'^admin', include('barres.photologue.urls')),                       
                           ) + urlpatterns

