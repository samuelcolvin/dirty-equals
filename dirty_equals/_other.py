from typing import Any, Literal
from uuid import UUID

from ._base import DirtyEquals
from ._utils import plain_repr


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
