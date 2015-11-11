import os
import elco


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DEBUG=True
ALLOWED_HOSTS = []

SECRET_KEY = 'n0t-s0-s3cr3t!'
DATABASES = {
    {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'tests'
] + elco.ELCO_CORE_APPS
