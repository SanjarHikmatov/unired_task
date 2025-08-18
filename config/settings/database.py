from config.settings.base import BASE_DIR

# Celery broker va backend
CELERY_BROKER_URL = "redis://127.0.0.1:6380/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6380/0"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
