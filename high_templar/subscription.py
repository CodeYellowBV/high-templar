"""
A subscriptions contains of three parts

(1) The connection (who is subscribed)
(2) The permission (where are we subscribted to)
(3) An identifier for this subscription (Such that we can subscribe more than once to the same object
"""
from collections import namedtuple

Subscription = namedtuple('Subscription', ['connection', 'request_id', 'permission'])
