from typing import Any, Optional, TypeVar

from ._base import DirtyEquals

B = TypeVar('B')


class IsFalseLike(DirtyEquals[B]):
    """
    Check if the value is False like. `IsFalseLike` allows comparison to anything and effectively uses
    `return not bool(other)` (with string checks if `allow_strings=True` is set).
    """

    def __init__(
        self,
        *,
        allow_strings: Optional[bool] = None,
    ):
        """
        Args:
            allow_strings: if `True`, allow comparisons to False like strings

        Example of basic usage:

        ```py title="IsFalseLike"
        from dirty_equals import IsFalseLike

        assert 'false' == IsFalseLike(allow_strings=True)
        assert 'foobar' != IsFalseLike(allow_strings=True)
        assert False == IsFalseLike
        assert 0 == IsFalseLike
        assert '0' == IsFalseLike(allow_strings=True)
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
        return other.lower() in {'0', '0.0', 'false'}
