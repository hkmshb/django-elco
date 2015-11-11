import os
import sys
from django.conf import settings

import elco



BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# django settings
settings.configure(
    DEBUG = True,
    ALLOWED_HOSTS = [],
    SECRET_KEY = 'n0t-s0-s3cr3t!',
    
    DATABASES = {
        'default': { 
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
        }
    },
    
    INSTALLED_APPS = [
        'django.contrib.contenttypes',
        'tests'
    ] + elco.ELCO_CORE_APPS,
    
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
    ),
)


if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
