from backend.settings import *
import dj_database_url

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default':  dj_database_url.config(
#         default=os.environ.get('EXTERNAL_DB_URL'),
#         conn_max_age=600,
#         conn_health_checks=True,
#     )
# }

INSTALLED_APPS += ['silk']

GZIP_MIDDLEWARE = 'django.middleware.gzip.GZipMiddleware'
if GZIP_MIDDLEWARE in MIDDLEWARE:
    sec_index = MIDDLEWARE.index(GZIP_MIDDLEWARE)
    MIDDLEWARE.insert(sec_index + 1, 'silk.middleware.SilkyMiddleware')
else:
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware') 

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Cors Config
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]

# Pusher
PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID_DEV')
PUSHER_KEY = os.environ.get('PUSHER_KEY_DEV')
PUSHER_SECRET = os.environ.get('PUSHER_SECRET_DEV')
PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')

# Silk
SILKY_PYTHON_PROFILER = True
SILKY_INTERCEPT_PERCENT = 100
