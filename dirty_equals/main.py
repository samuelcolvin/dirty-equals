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


class AnyInt:
    def __init__(self) -> None:
        self.v: Optional[int] = None

    def __eq__(self, other: Any) -> bool:
        if type(other) == int and not isinstance(other, bool):
            self.v = other
            return True
        else:
            return False

    def __repr__(self) -> str:
        if self.v is None:
            return '<AnyInt>'
        else:
            return repr(self.v)


AnyStr = TypeVar('AnyStr', str, bytes)


class RegexStr:
    def __init__(self, regex: AnyStr, flags: int = re.S) -> None:
        self._regex: Pattern[AnyStr] = re.compile(regex, flags=flags)  # type: ignore
        self.v: Optional[AnyStr] = None

    def __eq__(self, other: Any) -> bool:
        try:
            m = self._regex.fullmatch(other)
        except TypeError:
            pass
        else:
            if m:
                self.v = other
                return True

        return False

    def __repr__(self) -> str:
        if self.v is None:
            return f'<RegexStr(regex={self._regex!r}>'
        else:
            return repr(self.v)


class IsUUID:
    def __init__(self) -> None:
        self.v: Optional[UUID] = None

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, UUID):
            self.v = other
            return True
        else:
            # could also check for regex
            return False

    def __repr__(self) -> str:
        return repr(self.v) if self.v else '<UUID(*)>'
