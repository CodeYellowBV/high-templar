#! /usr/bin/env python3

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='high_templar',
    version='3.0.0',
    package_dir={'high_templar': 'high_templar'},
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A python framework for creating a server which handles websockets for an existing API',
    long_description=README,
    author='Code Yellow B.V.',
    author_email='pypi@codeyellow.nl',
    url='https://github.com/CodeYellowBV/high-templar',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'python-dotenv == 0.21.1',
        'aio-pika == 9.3.1',
        'hypercorn == 0.14.3',
        'quart == 0.11.2',
        'frozendict == 2.4.6',
        'aiohttp == 3.11.10',
        'Jinja2 == 3.0.3',
        'werkzeug == 2.1.2',
    ],
    test_suite='tests'
)
