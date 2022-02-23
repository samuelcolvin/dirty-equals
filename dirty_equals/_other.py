import json
from typing import Any, Callable
from uuid import UUID

from ._base import DirtyEquals
from ._utils import plain_repr

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]


class IsUUID(DirtyEquals[UUID]):
    """
    A class that checks if a value is a UUID. TODO.
    """

    def __init__(self, version: Literal[None, 1, 2, 3, 4, 5] = None):
        self.version = version
        super().__init__(version or plain_repr('*'))

    def equals(self, other: Any) -> bool:
        if isinstance(other, UUID):
            uuid = other
        elif isinstance(other, str):
            uuid = UUID(other, version=self.version or 4)
        else:
            return False

        if self.version:
            return uuid.version == self.version
        else:
            return True


AnyJson = object


class IsJson(DirtyEquals[Any]):
    """
    A class that checks if a value is a JSON object. TODO.
    """

    def __init__(self, expected_value: Any = AnyJson):
        self.expected_value = expected_value
        super().__init__(plain_repr('*') if expected_value is AnyJson else expected_value)

    def equals(self, other: Any) -> bool:
        if isinstance(other, (str, bytes)):
            v = json.loads(other)
            if self.expected_value is AnyJson:
                return True
            else:
                return v == self.expected_value
        else:
            return False


class FunctionCheck(DirtyEquals[Any]):
    """
    Use a function to check if a value "equals" whatever you want to check
    """

    def __init__(self, func: Callable[[Any], bool]):
        self.func = func
        super().__init__(plain_repr(func.__name__))

    def equals(self, other: Any) -> bool:
        return self.func(other)
