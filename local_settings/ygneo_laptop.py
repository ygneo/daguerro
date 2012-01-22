DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':  'daguerro',
        'USER': 'root',
        'PASSWORD': 'password',
        'DATABASE_HOST': 'localhost'
        }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

