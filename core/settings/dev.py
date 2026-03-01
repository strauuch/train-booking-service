from .base import *

DEBUG = env("DEBUG", default=True)
SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
