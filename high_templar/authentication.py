from typing import List
import json


class IncomparablePermisssionsException(Exception):
    pass


class Permission(dict):
    """
    Make a comparable object from permission
    """

    def __lt__(self, other: 'Permission'):
        # If the keys are not the same, we can not compare then
        if set(self.keys()) != set(other.keys()):
            return False

        # If we have the same keys, we can try to compare them
        for key in self.keys():
            # If the other permission has
            if other[key] == '*':
                continue

            if self[key] == '*':
                return False

            if self[key] != other[key]:
                return False

        return True

    def __gt__(self, other: 'Permission'):
        # If the keys are not the same, we can not compare then
        if set(self.keys()) != set(other.keys()):
            return False

        for key in self.keys():
            # If the other permission has
            if other[key] == '*':
                return False

            if self[key] == '*':
                continue

            if self[key] != other[key]:
                return False
        return True

    def __ge__(self, other):
        return self == other or self > other

    def __le__(self, other):
        return self == other or self < other


class Authentication:
    def __init__(self, allowed_rooms: List[Permission]):
        self.allowed_rooms = allowed_rooms

    def __str__(self):
        return "Authentication: Allowed rooms {}".format(json.dumps(self.allowed_rooms))

    def is_allowed(self, permission: Permission) -> bool:
        """
        Check if the user is allowed to subscribe on a room, based upon the allowed rooms

        :param room:
        :return:
        """
        pass
