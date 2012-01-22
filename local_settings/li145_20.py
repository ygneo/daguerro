DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':  'daguerro',
        'USER': 'root',
        'PASSWORD': 'rayuela7',
        'DATABASE_HOST': 'localhost'
        }
}

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/barres/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.barresfotonatura.com/barres/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/barres/admin_media/'


TINYMCE_JS_URL = MEDIA_URL + 'daguerro/js/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = MEDIA_ROOT + 'daguerro/js/tiny_mce'


