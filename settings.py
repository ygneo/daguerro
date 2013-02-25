#!/usr/bin/python
# -*- coding: utf-8 -*-

# Django settings for daguerro project.
import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Antonio Barcia', 'antonio.barcia@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = '<DB_NAME>'             # Or path to database file if using sqlite3.
DATABASE_USER = '<DB_USER>'             # Not used with sqlite3.
DATABASE_PASSWORD = '<DB_PASSWORD>'         # Not used with sqlite3.
DATABASE_HOST = 'localhost'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

STATIC_URL = "/static/"
STATIC_ROOT = "/var/www/barres/static/"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/barres/media/'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'oxadadwn7xx5yksdsop&93dasdas-d@1!!cz62^6-iadsda9a@0w@^!j5nl9^dasdaszpr5xr0w6e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS =(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',
    "daguerro.context_processors.current_site",
    "daguerro.context_processors.settings_processor",
    "website.context_processors.header_info",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'contrib.breadcrumbs.middleware.BreadcrumbsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

ROOT_URLCONF = 'barres.urls'

LOGIN_URL = '/daguerro/login/'
LOGIN_REDIRECT_URL = '/daguerro/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'templates')
)


INSTALLED_APPS = (
    'daguerro',
    'website',
    'form_utils',
    'photologue',
    'tinymce',
    'south',
    'debug_toolbar',
    'django_extensions',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'django_js_utils',
    'django_settings',
    'mptt',
    'haystack',
    'custom_fields',
)

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s [%(module)s] %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s [%(module)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'file':{
            'level':'DEBUG',
            'class':'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/daguerro/daguerro.log',
            'formatter': 'simple',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'daguerro': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'DEBUG',
        },
	'form_utils': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'DEBUG',
	}	
    }
}

# This setting can be overwritten in daguerro.settings
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'search_backends.search_engines.FoldingWhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

DAG_SEARCH_FIELDS_INITIAL = {"title": True, "tags": True, 
                             "cf_nombre_cientifico": True,
                             "cf_familia": True,
                             }
DAG_PHOTO_THUMB_SIZE_KEY = 'photo'
DAG_PHOTO_ORIGINAL_SIZE_KEY = 'original'
DAG_GALLERY_THUMB_SIZE_KEY = 'gallery'
DAG_NO_IMAGE = {DAG_PHOTO_ORIGINAL_SIZE_KEY: 'daguerro/img/no_picture_photo.png',
                DAG_PHOTO_THUMB_SIZE_KEY: 'daguerro/img/no_picture_photo.png',
                DAG_GALLERY_THUMB_SIZE_KEY: 'daguerro/img/no_picture_gallery.png'
                }

DAG_DEFAULT_PHOTO_ORDERING_FIELDS = [
    {'name': 'order', 'verbose_name': 'Manualmente'},
    {'name': 'title', 'verbose_name': 'Titulo'},
    {'name': 'date_added', 'verbose_name': 'Fecha de creacion'},
    {'name': 'cf_nombre_cientifico', 'verbose_name': 'Nombre cientifico'},
    {'name': 'cf_test', 'verbose_name': 'Test'},
    ]
DAG_DEFAULT_PHOTO_ORDERING = 'title'


THUMBNAIL_QUALITY = 95
THUMBNAIL_EXTENSION = 'png'

TINYMCE_DEFAULT_CONFIG = {'theme': "advanced", 
                          'relative_urls': False, 
                          'theme_advanced_buttons1' : "bold,italic,underline,strikethrough," \
                              "separator,fontsizeselect,separator,justifyleft,justifycenter," \
                              "justifyright,justifyfull,bullist,numlist,separator,cut,copy,paste," \
                              "undo,redo,separator,link,unlink,anchor",
                          'theme_advanced_buttons2': '',
                          'theme_advanced_buttons3': '',
                          'theme_advanced_toolbar_location' : 'top'}

MAPS_API_KEY = 'ABQIAAAApl773DNd8gKqDs88IJGhqxR1gbanoinoe2pNkEynQ_zYcd12shSqHBj5hvwPZUdIJHq1blEDrOIEHw'

DAGUERRO_CART_SESSION_KEY = 'daguerro-cart'

DAGUERRO_EMAIL_BODY =  u"""<p>Su pedido ha sido enviado correctamente y se atenderá en breve.</p>
                          <p>Para cualquier aclaración o consulta, escriba a %(email)s</p>"""

"""
Local settings importing
"""
try:
    import platform
    hostname = platform.node().replace('.','_').replace('-', '_')
    exec "from local_settings.%s import *" % hostname
except ImportError:
    pass

