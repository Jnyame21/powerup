from backend.settings import *
import dj_database_url
import os

DEBUG = False

ALLOWED_HOSTS = [
    'powerup-api.onrender.com',
]

DATABASES = {
    'default':  dj_database_url.config(
        default=os.environ.get('EXTERNAL_DB_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Cors Config
CORS_ALLOWED_ORIGINS = [
    "https://powerup.onrender.com",
]

# Pusher
PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')
PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID_PROD')
PUSHER_KEY = os.environ.get('PUSHER_KEY_PROD')
PUSHER_SECRET = os.environ.get('PUSHER_SECRET_PROD')
