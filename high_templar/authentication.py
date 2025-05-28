from typing import List
import json
from frozendict import frozendict
import logging

logger = logging.getLogger()

class IncomparablePermisssionsException(Exception):
    pass


class Permission(frozendict):
    """
    Make a comparable object from permission
    """

    def __lt__(self, other: 'Permission'):
        # If the keys are not the same, we can not compare then
        if set(self.keys()) != set(other.keys()):
            return False

        has_diff = False

        # If we have the same keys, we can try to compare them
        for key in self.keys():
            if self[key] == other[key]:
                continue
            # If the other permission has
            if other[key] == '*':
                has_diff = True
                continue

            if self[key] == '*':
                return False

            if self[key] != other[key]:
                return False
            has_diff = True

        return has_diff

    def __gt__(self, other: 'Permission'):
        # If the keys are not the same, we can not compare then
        if set(self.keys()) != set(other.keys()):
            return False

        # in order to be different, we need one diff at least
        has_diff = False

        for key in self.keys():
            if self[key] == other[key]:
                continue

            if other[key] == '*':
                return False

            if self[key] == '*':
                has_diff = True
                continue
            return False


        return has_diff

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other

    # Room names are dict.
    # Every keyval pair is a scope of the permission.
    # IE:
    # { 'zoo': 1, 'animal_type': 'penguin'}
    # Is a room where publishes about the penguins in zoo 1 appear.
    #
    # The backend needs to dictate which rooms a user can be in,
    # and the frontend needs to programmatically define the room to subscribe to.
    #
    # We hash the dicts so that
    # {'foo': True, 'bar': True} is the same room as {'bar': True, 'foo': True}
    # and so we can still check if a room exists
    def hash(self):
        unfrozen = {}

        for key in self.keys():
            unfrozen[key] = self[key]

        return json.dumps(unfrozen, sort_keys=True)



class Authentication:
    def __init__(self, allowed_rooms: List[Permission]):
        self.allowed_rooms = set(allowed_rooms)

    def json_serializable(self):
        return list(map(lambda r: dict(r), self.allowed_rooms))

    def __str__(self):
        return "Authentication: Allowed rooms {}".format(json.dumps(self.json_serializable()))

    """
    TODO:

    this currently is a O(N * M) algorithm, with N = amount of permission and M = #keys in permission

    This can be optimized further with making a tree of the keys, with hashsets in the nodes. That would allow to traverse
    the tree in O(M * 1) = O(M) time,

    This only makes sense if the amount of has_permission checks outweights the amount of times connected

    """
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the user is allowed to subscribe on a room, based upon the allowed rooms

        :param room:
        :return:
        """

        if permission in self.allowed_rooms:
            return True

        for p in self.allowed_rooms:
            # Check if we have at least one permission that is bigger than the request permission
            if p >= permission:
                return True

        return False
