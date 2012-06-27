DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':  'barres',
        'USER': 'root',
        'PASSWORD': 'root',
        'DATABASE_HOST': 'localhost'
        }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

