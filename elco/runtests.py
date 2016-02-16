"""
A stand-alone test runner script, configuring the minimum settings required for
tests to execute.
"""
import os
import sys


# ensure app is found on the import path
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, BASE_DIR)


# minimum settings required for app's tests
SETTINGS_DICT = {
    'BASE_DIR': BASE_DIR,
    'INSTALLED_APPS': (
        'address',
        'elco',
    ),
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, '..', 'db.sqlite3'),
        },
    },
}


def run_tests():
    # two-step activation to get Django tests to run. First, call
    # settings.configure() to give Django settings to work with
    from django.conf import settings
    settings.configure(**SETTINGS_DICT)
    
    # Then, call django.setup() to initialize the application cache
    # and other parts:
    import django
    if hasattr(django, 'setup'):
        django.setup()
    
    # now instantiate a test runner
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    
    # now we run the tests..
    test_runner = TestRunner(verbosity=1, interactive=True)
    failures = test_runner.run_tests(['elco.tests'])
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests()

