from .base import *

ALLOWED_HOSTS = ['*']
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = []
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pybo',
        'USER': 'dbmasteruser',
        'PASSWORD': '=eKmx$xxymnxxwNCxxx$SX55*RdjKK1G&',
        'HOST': 'ls-be78fd2cxxxxx614420dxxxxx6b156e2c9.cqlcyugj7ibs.ap-northeast-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}
