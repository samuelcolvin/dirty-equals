import re
from typing import Any, Optional, Pattern, TypeVar, Union

from ._base import DirtyEquals

T = TypeVar('T', str, bytes)


class IsStrBase(DirtyEquals[T]):
    types: type = NotImplemented

    # TODO min_length, max_length, upper, lower, digits
    def __init__(self, *, regex: Union[None, T, Pattern[T]] = None, regex_flags: re.RegexFlag = re.S) -> None:
        self.regex: Union[None, T, Pattern[T]] = regex
        self.regex_flags = regex_flags
        super().__init__(regex=regex, regex_flags=regex_flags)

    def equals(self, other: Any) -> bool:
        if type(other) != self.types:
            return False
        elif self.regex is not None and not re.fullmatch(self.regex, other, flags=self.regex_flags):  # type: ignore
            return False
        else:
            return True


class IsStr(IsStrBase[str]):
    types = str


class IsBytes(IsStrBase[bytes]):
    types = bytes


class IsAnyStr(DirtyEquals[Union[str, bytes]]):
    def __init__(self, *, regex: Union[str, bytes] = None, regex_flags: re.RegexFlag = re.S) -> None:
        if isinstance(regex, str):
            self.regex: Optional[bytes] = regex.encode()
        else:
            self.regex = regex
        self.regex_flags = regex_flags
        super().__init__(regex=regex, regex_flags=regex_flags)

    def equals(self, other: Any) -> bool:
        if type(other) not in (str, bytes):
            return False
        elif self.regex is not None:
            if isinstance(other, str):
                other = other.encode()
            return bool(re.fullmatch(self.regex, other, flags=self.regex_flags))
        else:
            return False
