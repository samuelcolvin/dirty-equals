import re
from datetime import datetime, timezone
from typing import Any, Optional, Pattern, TypeVar
from uuid import UUID

__all__ = 'CloseToNow', 'AnyInt', 'RegexStr', 'IsUUID'


class CloseToNow:
    def __init__(self, delta: int = 2) -> None:
        self.delta: float = delta
        self.now = datetime.utcnow()
        self.match = False
        self.other = None

    def __eq__(self, other: Any) -> bool:
        self.other = other
        if not isinstance(other, datetime):
            try:
                from pydantic.datetime_parse import parse_datetime
            except ImportError:  # pragma: no cover
                raise ImportError('pydantic is required to use CloseToNow, please run `pip install pydantic`')
            other = parse_datetime(other)
        if other.tzinfo:
            self.now = self.now.replace(tzinfo=timezone.utc)
        self.match = -self.delta < (self.now - other).total_seconds() < self.delta
        return self.match

    def __repr__(self) -> str:
        if self.match:
            # if we've got the correct value return it to aid in diffs
            return repr(self.other)
        else:
            # else return something which explains what's going on.
            return f'<CloseToNow(delta={self.delta}, now={self.now:%Y-%m-%dT%H:%M:%S})>'
