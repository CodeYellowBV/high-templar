high-templar
====================

A python framework for creating a stateful server which handles websocket functionality for an existing django instance.

Motivation
------

Django doesn't support websockets out of the box. To add websocket support to Django, one can either:

* Monkey patch the Django WSGI server to use greenlets, and add websocket support using gevent-websockets. Django however doesn't handle microthreads very well, and gevent-websockets is untested.
* Use django-channels which puts websocket traffic onto a redis queue, and uses workers which pop the queue and feed the messages to Django. Managing the workers which interact with the queue can however provide major headaches.

High-templar uses a similar approach to django-channels, but uses internal HTTP requests to communicate with the existing Django instance. High-templar keeps track of the active websocket connections, which allows the Django instance to remain stateless.

|architecture|


.. |architecture| image:: architecture.png
