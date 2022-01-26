import re
from datetime import datetime, timezone
from uuid import UUID


class CloseToNow:
    def __init__(self, delta=2):
        self.delta: float = delta
        self.now = datetime.utcnow()
        self.match = False
        self.other = None

    def __eq__(self, other):
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

    def __repr__(self):
        if self.match:
            # if we've got the correct value return it to aid in diffs
            return repr(self.other)
        else:
            # else return something which explains what's going on.
            return f'<CloseToNow(delta={self.delta}, now={self.now:%Y-%m-%dT%H:%M:%S})>'


class AnyInt:
    def __init__(self):
        self.v = None

    def __eq__(self, other):
        if type(other) == int and not isinstance(other, bool):
            self.v = other
            return True
        else:
            return False

    def __repr__(self):
        if self.v is None:
            return '<AnyInt>'
        else:
            return repr(self.v)


class RegexStr:
    def __init__(self, regex, flags=re.S):
        self._regex = re.compile(regex, flags=flags)
        self.v = None

    def __eq__(self, other):
        if self._regex.fullmatch(other):
            self.v = other
            return True
        else:
            return False

    def __repr__(self):
        if self.v is None:
            return f'<RegexStr(regex={self._regex!r}>'
        else:
            return repr(self.v)


class IsUUID:
    def __init__(self):
        self.v = None

    def __eq__(self, other):
        if isinstance(other, UUID):
            self.v = other
            return True
        else:
            # could also check for regex
            return False

    def __repr__(self):
        return repr(self.v) if self.v else '<UUID(*)>'
