import json
from typing import List

from high_templar.authentication import Authentication


class BackendConnectionException(Exception):
    pass


class NoBackendConnectionException(BackendConnectionException):
    pass


class UnparsableBackendPermissionsException(BackendConnectionException):
    pass


class BackendAdapter:
    async def get_authentication(self, headers) -> Authentication:
        pass
