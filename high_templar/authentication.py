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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_set = set(self.keys())

    def __lt__(self, other: 'Permission'):
        # If the keys are not the same, we can not compare then
        if self.key_set != other.key_set:
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
                logger.error('HIer 1')
                return False

            if self[key] != other[key]:
                logger.error('HIer 2')
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


class Authentication:
    def __init__(self, allowed_rooms: List[Permission]):
        self.allowed_rooms = allowed_rooms

    def json_serializable(self):
        return list(map(lambda r: dict(r), self.allowed_rooms))

    def __str__(self):
        return "Authentication: Allowed rooms {}".format(json.dumps(self.json_serializable()))

    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the user is allowed to subscribe on a room, based upon the allowed rooms

        :param room:
        :return:
        """
        for p in self.allowed_rooms:
            # Check if we have at least one permission that is bigger than the request permission
            logger.error(f">>> {p} {permission}, {p >= permission}")
            if p >= permission:
                return True

        return False
