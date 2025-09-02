import os

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE'),
        'USER': os.environ.get('PGUSER'),
        'PASSWORD': os.environ.get('PGPASSWORD'),
        'HOST': os.environ.get('PGHOST'),
        'PORT': os.environ.get('PGPORT'),
    }
}

