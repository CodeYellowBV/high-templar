from abc import ABC, abstractmethod

from werkzeug.http import parse_cookie


class NoValue(ValueError):
    pass


class Header(ABC):

    @abstractmethod
    def get_value(self, environ):
        """
        Given an environ return either a value for a header or raise a
        NoValue exception if no value could be deduced from the environ.
        """

    def map(self, func):
        return Map(func, self)


class Key(Header):
    """
    Use a key from the environ directly.
    """

    def __init__(self, key):
        self._key = key

    def get_value(self, environ):
        if self._key not in environ:
            raise NoValue
        return environ[self._key]


class Param(Header):
    """
    Use the value of a GET param on the original request.
    """

    def __init__(self, key):
        self._key = key

    def get_value(self, environ):
        request = environ.get('werkzeug.request', None)
        if not request or self._key not in request.args:
            raise NoValue
        return request.args[self._key]


class Cookie(Header):
    """
    Use the value of a cookie on the original request.
    """

    def __init__(self, key):
        self._key = key

    def get_value(self, environ):
        try:
            cookie = parse_cookie(environ['HTTP_COOKIE'])
            return cookie[self._key]
        except KeyError as e:
            raise NoValue


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

    def get_value(self, environ):
        args = [
            value.get_value(environ)
            for value in self._args
        ]
        kwargs = {
            key: value.get_value(environ)
            for key, value in self._kwargs.items()
        }
        return self._func(*args, **kwargs)
