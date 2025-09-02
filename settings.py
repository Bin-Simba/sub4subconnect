import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

CORS_ALLOWED_ORIGINS = [
    "https://sub4subyoutube.netlify.app/",
    "http://127.0.0.1:5173",  # Keep this if you still want to allow local dev
]

CSRF_TRUSTED_ORIGINS = [
    "https://sub4subyoutube.netlify.app/",
    "http://127.0.0.1:5173",  # Keep this if you still want to allow local dev
]

ALLOWED_HOSTS = [
    "sub4subyoutube.netlify.app",
    "127.0.0.1",  # Keep this if you still want to allow local dev
    "localhost",  # Optional: remove if you want to block localhost
    "0.0.0.0",
]

# Database configuration
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Security settings for production
DEBUG = False
ALLOWED_HOSTS = ['*']  # Or specify your domain

# Static files with WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE = [
    # ...existing middleware...
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...existing middleware...
]

# Allow all Railway domains
ALLOWED_HOSTS = [
    'sub4subconnect-production.up.railway.app',
    '.railway.app',  # Allows all Railway subdomains
]

# For development, you can also allow localhost
# ALLOWED_HOSTS = ['*']  # ⚠️ Only for testing, not production!
