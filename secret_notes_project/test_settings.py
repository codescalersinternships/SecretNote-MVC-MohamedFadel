import tempfile

from .settings import *

STATIC_ROOT = tempfile.mkdtemp()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

DEBUG = True
ALLOWED_HOSTS = ["*"]
