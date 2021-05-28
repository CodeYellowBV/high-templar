====================
high-templar
====================

|build_status|_ |code_coverage|_

A python framework for creating a stateful server which handles websocket functionality for an existing HTTP only API.

Flow
=======


- A client opens a websocket connection with a High-templar instance.
- The HT instance proxies the request to the API, which in turn handles authentication and provides a list of rooms.
- The HT instance tells the client what rooms he is allowed to subscribe to.
- The client subscribes to one or more rooms
- When receiving a trigger from the API, the HT instance publishes the received data to the specified rooms.



Installation
==============



.. code:: bash

    pip install -Ur requirements.txt
    pip install high-templar

    # Install rabbitmq and create a user.
    apt install rabbitmq-server
    rabbitmqctl add_user rabbitmq rabbitmq
    rabbitmqctl set_user_tags rabbitmq administrator
    rabbitmqctl set_permissions -p / rabbitmq ".*" ".*" ".*"

    # Take a look at `install` folder for examples for systemd.


Motivation
==============


This project is created for handling websockets for a django instance.
Django doesn't support websockets out of the box. To add websocket support to Django, one can either
monkey patch the Django WSGI with gevent, or use django-channels which requires a lot of configuration and needs you to manage its workers.

High-templar uses a similar approach to django-channels, but uses internal HTTP requests to communicate with the existing Django instance. High-templar keeps track of the active websocket connections, which allows the Django instance to remain stateless.

Architecture
==============


|architecture|_

The Rabbitmq rewrite made it possible


2 concepts are fundamental:

1. Connection: a single websocket bi-directional data pipe connection.
2. Room: an authenticated place where data is send from the server.


Normally only 1 connection is created during the entire session, but many, many rooms are subscribed to using this single connection. When a connection is created, the server responds with the allowed rooms for that user. A room is identified by a hash, and upon subscribing the client needs to specify a unique `requestId` that identifies the subscription to that room. That `requestId` can be used to match messages send from the server to a specific room. It is also used to unsubscribe from a room.





Interfaces
==============


Starting a connection
------------------------

Starting up a connection

When creating a connection, and authentication can be done:

Response:

.. code:: json

    {
        "is_authenticated": True,
        "allowed_rooms": [{
            "target": "message",
            "customer": "1"
        }]
    }

When creating a connection, and authentication can not be done:

Response:

.. code:: json

    {
        "is_authenticated": False
    }


Subscribing to a room
------------------------

Request:

.. code:: json
    {
        "type": "subscribe",
        "room": {
            "target": "message",
            "customer": "1"
        },
        "requestId": "1"
    }

Response when you have permission:

.. code:: json
    { "code": "success" }


Response when you don't have permission or the room doesn't exist:

.. code:: json
    {
        "code": "error",
        "message": "room-not-found"
    }


TODO: document unsubscribe


Room permissions
------------------------

The initial message send from the server contains an `allowed_rooms` key. This `allowed_rooms` key determines which rooms which the client can subscribe to. Upon subscribing, the server checks if the client is allowed into the room, but once connected no futher permission checking is done. An example server response upon creating a connection:


.. code:: json
    {
        "is_authenticated": True,
        "allowed_rooms": [{
            "room": "user-login",
            "department": "finance"
        }, {
            "room": "user-logout",
            "department": "finance"
        }, {
            "target": "chat-create",
            "customer": "*"
        }, {
            "target": "chat-update",
            "customer": "*"
        }]
    }


The key / value pairs have no meaning, other then identifying a room. An exception is the special `*` character, which means that anything will match in place of that character. For the response above, it means the client can connect to the 4 rooms described in `allowed_rooms`, but also to:

.. code:: json
    {
        "type": "subscribe",
        "room": {
            "target": "chat-create",
            "customer": "*"
        },
        "requestId": "1"
    }

.. code:: json
    {
        "type": "subscribe",
        "room": {
            "target": "chat-create",
            "customer": "1"
        },
        "requestId": "2"
    }

.. code:: json
    {
        "type": "subscribe",
        "room": {
            "target": "chat-create",
            "customer": "2"
        },
        "requestId": "3"
    }


Sending data to a room
------------------------


To send data to a room, send a POST request to the server:

.. code:: json
    {
        [
            {
                "target": "chat-create",
                "customer": "*"
            },
            {
                "target": "chat-create",
                "customer": "1"
            },
            {
                "target": "chat-create",
                "customer": "2"
            }
        ],
        "data": "Example text body"
    }


Using the `*`, we can cut 2 rooms. So this is the exactly the same as:

.. code:: json
    {
        [
            {
                "target": "chat-create",
                "customer": "*"
            }
        ],
        "data": "Example text body"
    }

TODO: Implement this
TODO: Add test for trigger http endpoint



Ping pong
------------------------

The frontend can send a ping message to check if the websocket connection is still working.
HT will send a pong message if the connection is still open

Request:

.. code:: text

    ping

Response:

.. code:: text

    pong

Tests
=======

Run high templar first:
`./run`

After it is started, you can run all tests:
`./test`

Or run a specific test:
`./test -v tests/tests/test_unsubscribe.py::TestUnSubscribe::test_unsubscribe_to_room`

Origin
=======

This repository is based on archon_. Archon is a framework for creating full fledged websocket based CRUD APIs. High-templar is only half the framework of Archon, as it relies on an existing API and only provides pubsub.


.. |architecture| image:: architecture.png
.. _archon: https://github.com/JasperStam/archon
.. |build_status| image:: https://travis-ci.org/CodeYellowBV/high-templar.svg?branch=master
.. _build_status: https://travis-ci.org/CodeYellowBV/high-templar
.. |code_coverage| image:: https://codecov.io/gh/CodeYellowBV/high-templar/branch/master/graph/badge.svg
.. _code_coverage: https://codecov.io/gh/CodeYellowBV/high-templar

