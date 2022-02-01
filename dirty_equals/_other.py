import json
from typing import Any
from uuid import UUID

from ._base import DirtyEquals
from ._utils import plain_repr

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]


class IsUUID(DirtyEquals[UUID]):
    def __init__(self, version: Literal[None, 1, 2, 3, 4, 5] = None):
        self.version = version
        super().__init__(version or plain_repr('*'))

    def equals(self, other: Any) -> bool:
        if isinstance(other, UUID):
            if self.version:
                return other.version == self.version
            else:
                return True
        elif isinstance(other, str):
            try:
                uuid = UUID(other, version=self.version or 4)
            except ValueError:
                return False
            else:
                self._other = uuid
                return True
        else:
            return False


AnyJSON = object


class IsJSON(DirtyEquals[str]):
    def __init__(self, expected_value: Any = AnyJSON):
        self.expected_value = expected_value
        super().__init__(plain_repr('*') if expected_value is AnyJSON else expected_value)

    def equals(self, other: Any) -> bool:
        if isinstance(other, (str, bytes)):
            v = json.loads(other)
            if self.expected_value is AnyJSON:
                return True
            else:
                return v == self.expected_value
        else:
            return False
