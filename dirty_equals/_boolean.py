from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union, _SpecialForm

from ._base import DirtyEquals

B = TypeVar('B', int, bool, str, float, List[Any], Dict[Any, Any], Set[Any], Tuple[Any], Type[None])


class IsFalseLike(DirtyEquals[B]):
    """
    Check if the value is False like, and matches the given conditions.
    """

    allowed_types: Union[Type[B], Tuple[Union[_SpecialForm, type], ...]] = (
        int,
        bool,
        str,
        float,
        List,
        Dict,
        Set,
        type(None),
        Tuple,
    )

    def __init__(
        self,
        numeric: Optional[bool] = None,
        string: Optional[bool] = None,
    ):
        """
        Example of basic usage:

        ```py title="IsFalseLike"
        from dirty_equals import IsFalseLike

        assert False == IsFalseLike
        assert 0 == IsFalseLike(numeric=True)
        assert '0' == IsFalseLike(string=True)
        assert 'True' != IsFalseLike(string=True)
        assert [1] != IsFalseLike
        assert {} == IsFalseLike
        assert None == IsFalseLike
        assert 'False' == IsFalseLike(string=True)
        ```
        """
        self.numeric: Optional[bool] = numeric
        self.string: Optional[bool] = string
        if self.numeric and self.string:
            raise TypeError('"numeric" and "string" cannot be combined')
        if self.numeric and not isinstance(self.numeric, bool):
            raise ValueError('"numeric" requires a boolean argument')
        if self.string and not isinstance(self.string, bool):
            raise ValueError('"string" requires a boolean argument')
        super().__init__(
            numeric=numeric,
            string=string,
        )

    def equals(self, other: Any) -> bool:
        if not isinstance(other, self.allowed_types):  # type: ignore[arg-type]
            raise TypeError(f'not a {self.allowed_types}')
        if self.numeric:
            return self.make_numeric_check(other)
        if self.string:
            return self.make_string_check(other)
        if other in ([], {}, (), set(), False, None):
            return True
        return False

    @staticmethod
    def make_numeric_check(other: B) -> bool:
        if other in (0, 0.0):
            return True
        else:
            return False

    @staticmethod
    def make_string_check(other: B) -> bool:
        if other in ('0', '0.0', 'False'):
            return True
        else:
            return False
