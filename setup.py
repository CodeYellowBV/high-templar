#! /usr/bin/env python3

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

setup(
    name='high_templar',
    version='2.4.0',
    packages=find_packages(include=['high_templar', 'high_templar.*']),
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'gevent >= 1.1.2, < 1.4.0',
        'greenlet >= 0.4.12',
        'Flask >= 0.12.0',
        'Flask-Sockets >= 0.2.1',
        'python-dotenv >= 0.6.3',
        'requests >= 2.13.0',
    ],
    test_suite='tests'
)
