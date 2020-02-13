from typing import List


class Authentication:
    def __init__(self, allowed_rooms: List):
        self.allowed_rooms = allowed_rooms

    def __str__(self):
        return "Authentication: Allowed rooms {}".format(",".join(self.allowed_rooms))


class BackendConnectionException(Exception):
    pass


class NoBackendConnectionException(BackendConnectionException):
    pass


class BackendAdapter:
    async def get_authentication(self, headers) -> Authentication:
        pass
