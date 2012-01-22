from django.conf.urls.defaults import *

# Generic views
urlpatterns = patterns(
    '',
    (r'login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'logout/$', 'django.contrib.auth.views.logout_then_login'),
)

# App-specific views
urlpatterns += patterns(
    'daguerro.views',
    # Index Gallery urls
    (r'^$', 'index', {'slugs': None}, 'daguerro-gallery'),
    (r'^gallery/$', 'index', {'slugs': None}, 'daguerro-gallery'),
    
    # Photo handling urls
    url(r'^gallery/(?P<slugs>.+)?/photo/add', 'photo', name='daguerro-gallery-photo-add'),
    url(r'^gallery/photo/add/$','photo', name='daguerro-gallery-photo-add-root'),
    url(r'^gallery/(?P<slugs>.+)/foto/(?P<slug>.+)$', 'photo', {'action': 'edit'}, name='daguerro-gallery-photo'),
    url(r'^gallery/(?P<slugs>.+)/photo/(?P<id>\d+)/delete$', 'photo_delete', name='daguerro-photo-delete'),

    # Gallery handling urls
    url(r'^gallery/(?P<slugs>.+)?/add$', 'gallery', name='daguerro-gallery-add'),
    url(r'^gallery/add', 'gallery', {'slugs': None, 'action': 'add'}, name='daguerro-gallery-add'),
    url(r'^gallery/(?P<slugs>.+)?/edit$', 'gallery', {'action': 'edit'}, name='daguerro-gallery-edit'),
    url(r'^gallery/(?P<slugs>.+)/delete$', 'gallery_delete', name='daguerro-gallery-delete'),
    url(r'^gallery/(?P<gallery_id>\d+)/add-photo/(?P<photo_id>\d+)$', 'add_photo'),
    url(r'^gallery/(?P<slugs>.+)$', 'index', name='daguerro-gallery'),

    # Searching urls
    url(r'^search-photo\.?(?P<format>json|html)?', 'search_photo',  name='daguerro-search-photo'),

    # Sorting url
    url(r'^sort-items', 'sort_items',  name='daguerro-sort-items'),

    # Pages urls
    url(r'^page/$', 'pages_index',  name='daguerro-pages-index'),
    url(r'^page/add', 'page', {'action': 'add'}, name='daguerro-page-add'),
    url(r'^page/(?P<id>\d+)', 'page', {'action': 'edit'}, name='daguerro-page'),

    # Users urls
    url(r'^user/$', 'users_index',  name='daguerro-users-index'),
    url(r'^user/add', 'user', {'action': 'add'}, name='daguerro-user-add'),
    url(r'^user/(?P<id>\d+)/password/$', 'user_change_password', name='daguerro-user-change-password'),
    url(r'^user/(?P<id>\d+)/', 'user', {'action': 'edit'}, name='daguerro-user'),
)
