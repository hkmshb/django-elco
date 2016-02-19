import os
from setuptools import setup



version = '0.0'

setup(
    name='django-elco',
    version=version,
    zip_safe=False,
    
    author='Abdul-Hakeem Shaibu',
    author_email='hkmshb@gmail.com',
    url='https://github.com/hkmshb/django-elco',
    description='',
    long_description=open(os.path.join(os.path.dirname(__file__), 
                                       'README.md')).read(),
    packages=['elco'],
    test_suite='elco.runtests.run_tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django 1.8',
        'Framework :: Django 1.9',
        'Intended Audience :: Developers',
        'License ::',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
