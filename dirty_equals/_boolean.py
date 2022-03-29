from typing import Any, Optional

from ._base import DirtyEquals


class IsTrueLike(DirtyEquals[bool]):
    """
    Check if the value is True like. `IsTrueLike` allows comparison to anything and effectively uses just
    `return bool(other)`.
    """

    def __init__(self) -> None:
        """
        Example of basic usage:

        ```py title="IsTrueLike"
        from dirty_equals import IsTrueLike

        assert True == IsTrueLike
        assert 1 == IsTrueLike
        assert 'true' == IsTrueLike
        assert 'foobar' == IsTrueLike  # any non-empty string is "True"
        assert '' != IsTrueLike
        assert [1] == IsTrueLike
        assert {} != IsTrueLike
        assert None != IsTrueLike
        ```
        """
        super().__init__()

    def equals(self, other: Any) -> bool:
        return bool(other)


class IsFalseLike(DirtyEquals[bool]):
    """
    Check if the value is False like. `IsFalseLike` allows comparison to anything and effectively uses
    `return not bool(other)` (with string checks if `allow_strings=True` is set).
    """

    def __init__(self, *, allow_strings: bool = False):
        """
        Args:
            allow_strings: if `True`, allow comparisons to `False` like strings, case-insensitive, allows
                `'false'` and any string where `float(other) == 0` (e.g. `'0'`).

        Example of basic usage:

        ```py title="IsFalseLike"
        from dirty_equals import IsFalseLike

        assert False == IsFalseLike
        assert 0 == IsFalseLike
        assert 'false' == IsFalseLike(allow_strings=True)
        assert '0' == IsFalseLike(allow_strings=True)
        assert 'foobar' != IsFalseLike(allow_strings=True)
        assert 'false' != IsFalseLike
        assert 'True' != IsFalseLike(allow_strings=True)
        assert [1] != IsFalseLike
        assert {} == IsFalseLike
        assert None == IsFalseLike
        ```
        """
        self.allow_strings: Optional[bool] = allow_strings
        super().__init__(allow_strings=allow_strings)

    def equals(self, other: Any) -> bool:
        if isinstance(other, str) and self.allow_strings:
            return self.make_string_check(other)
        return not bool(other)

    @staticmethod
    def make_string_check(other: str) -> bool:
        if other.lower() == 'false':
            return True

        try:
            return float(other) == 0
        except ValueError:
            return False
