import os
from .base import *

DEBUG = False

ADMINS = [
    ("Antonio M", "email@mydomain.com"),
]

ALLOWED_HOSTS = ['.educaproject.com']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": 5432,
    }
}
REDIS_URL = "redis://cache:6379"
CACHES["default"]["LOCATION"] = REDIS_URL
CHANNEL_LAYERS["default"]["CONFIG"]["hosts"] = [REDIS_URL]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True # cookie и csrf только по https
SECURE_SSL_REDIRECT = True # http запросы будут redirect на https
