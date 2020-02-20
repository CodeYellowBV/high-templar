from abc import ABC, abstractmethod

from werkzeug.datastructures import Headers
from werkzeug.http import parse_cookie


class NoValue(ValueError):
    pass


class Header(ABC):

    @abstractmethod
    def get_value(self, websocket):
        """
        Given an environ return either a value for a header or raise a
        NoValue exception if no value could be deduced from the environ.
        """
        pass

    def map(self, func):
        return Map(func, self)


class Key(Header):
    """
    Use a key from the environ directly.
    """

    def __init__(self, key):
        self._key = key

    def get_value(self, websocket):
        value = websocket.headers.get(self._key, None)

        if not value:
            raise NoValue
        return value


class Param(Header):
    """
    Use the value of a GET param on the original request.
    """

    def __init__(self, key):
        self._key = key

    def get_value(self, websocket):
        value = websocket.args.get(self._key, None)

        if not value:
            raise NoValue("value: {} {}".format(self._key, value))
        return value


class Cookie(Header):
    """
    Use the value of a cookie on the original request.
    """

    def __init__(self, key):
        self._key = key
        self._cookie_key = Key('Cookie')

    def get_value(self, websocket):
        try:
            cookie = parse_cookie(self._cookie_key.get_value(websocket))
        except KeyError:
            raise NoValue
        if self._key not in cookie:
            raise NoValue
        return cookie[self._key]


class Fixed(Header):
    """
    Use a fixed value as value.
    """

    def __init__(self, value):
        self._value = value

    def get_value(self, environ):
        return self._value


class Map(Header):
    """
    Transform a header object's value to get a new value.
    """

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def get_value(self, websocket):
        args = [
            value.get_value(websocket)
            for value in self._args
        ]
        kwargs = {
            key: value.get_value(websocket)
            for key, value in self._kwargs.items()
        }
        return self._func(*args, **kwargs)
