from core.settings.settings import *
import os
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Set SECRET_KEY in the production environment.")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
]
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Set DJANGO_ALLOWED_HOSTS or deploy on Render with RENDER_EXTERNAL_HOSTNAME."
    )
if "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Do not use a wildcard in production DJANGO_ALLOWED_HOSTS.")

if not os.getenv("CLOUDINARY_URL"):
    raise ImproperlyConfigured(
        "Set CLOUDINARY_URL to a persistent media storage service."
    )

STORAGES["default"] = {
    "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
}

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = False

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS.extend(
    f"https://{host}" for host in ALLOWED_HOSTS if host != "*"
)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ImproperlyConfigured("Set DATABASE_URL to a persistent production database.")

DATABASES = {
    'default': dj_database_url.config(
        default=database_url,
        conn_max_age=600,
    )
}