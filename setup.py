#! /usr/bin/env python3

import os
from setuptools import find_packages, setup

# with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
#     README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='chimera-cub',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A server which handles websockets for an existing django-binder instance',
    author='Jasper Stam',
    author_email='jasper@codeyellow.nl',
    url='https://github.com/CodeYellowBV/chimera-cub',
    classifiers=[],
    install_requires=[
        'gevent >= 1.1.2',
        'Flask >= 0.12.0',
        'Flask-Script >= 2.0.5',
        'Flask-Sockets >= 0.2.1',
        'python-dotenv >= 0.6.3',
        'requests >= 2.13.0',
    ],
    test_suite='tests',
)
