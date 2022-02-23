import re
from typing import Any, Optional, Pattern, Type, TypeVar, Union

from ._base import DirtyEquals
from ._utils import Omit

T = TypeVar('T', str, bytes)


class IsStrBytesBase(DirtyEquals[T]):
    expected_type: Type[T]

    # TODO min_length, max_length, upper, lower, digits
    def __init__(self, *, regex: Union[None, T, Pattern[T]] = None, regex_flags: re.RegexFlag = re.S):
        self.regex: Union[None, T, Pattern[T]] = regex
        self.regex_flags = regex_flags
        super().__init__(regex=regex or Omit, regex_flags=Omit if regex_flags == re.S else regex_flags)

    def equals(self, other: Any) -> bool:
        if type(other) != self.expected_type:
            return False
        elif self.regex is not None and not re.fullmatch(self.regex, other, flags=self.regex_flags):
            return False
        else:
            return True


class IsStr(IsStrBytesBase[str]):
    """
    Checks if the value is a string. TODO.
    """

    expected_type = str


class IsBytes(IsStrBytesBase[bytes]):
    """
    Checks if the value is a bytes object. TODO.
    """

    expected_type = bytes


class IsAnyStr(DirtyEquals[Union[str, bytes]]):
    """
    Checks if the value is a string or bytes object. TODO.
    """

    def __init__(self, *, regex: Union[None, str, bytes] = None, regex_flags: re.RegexFlag = re.S):
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
            return True
