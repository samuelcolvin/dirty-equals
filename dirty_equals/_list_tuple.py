from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sized, Tuple, Type, TypeVar, Union, overload

from ._base import DirtyEquals
from ._utils import Omit, plain_repr

if TYPE_CHECKING:
    from typing import TypeAlias

__all__ = 'HasLen', 'IsListOrTuple', 'IsList', 'IsTuple'
T = TypeVar('T', List[Any], Tuple[Any, ...])
LengthType: 'TypeAlias' = 'Union[None, int, Tuple[int, Union[int, Any]]]'


class HasLen(DirtyEquals[Sized]):
    @overload
    def __init__(self, length: int):
        ...

    @overload
    def __init__(self, min_length: int, max_length: Union[int, Any]):
        ...

    def __init__(self, min_length: int, max_length: Union[None, int, Any] = None):  # type: ignore[misc]
        if max_length is None:
            self.length: 'LengthType' = min_length
            super().__init__(self.length)
        else:
            self.length = (min_length, max_length)
            super().__init__(*_length_repr(self.length))

    def equals(self, other: Any) -> bool:
        return _length_correct(self.length, other)


class IsListOrTuple(DirtyEquals[T]):
    expected_type: Union[Type[T], Tuple[Type[List[Any]], Type[Tuple[Any, ...]]]] = (list, tuple)

    @overload
    def __init__(self, *items: Any, check_order: bool = True, length: 'LengthType' = None):
        ...

    @overload
    def __init__(self, positions: Dict[int, Any], length: 'LengthType' = None):
        ...

    def __init__(
        self,
        *items: Any,
        positions: Optional[Dict[int, Any]] = None,
        check_order: bool = True,
        length: 'LengthType' = None,
    ) -> None:
        if positions is not None:
            self.positions: Optional[Dict[int, Any]] = positions
            if items:
                raise TypeError(f'{self.__class__.__name__} requires either args or positions, not both')
            if not check_order:
                raise TypeError('check_order=False is not compatible with positions')
        else:
            self.positions = None
            self.items = items
        self.check_order = check_order

        self.length = length
        if self.length is not None and not isinstance(self.length, int):
            self.length = tuple(self.length)  # type: ignore[assignment]

        super().__init__(
            *items,
            positions=Omit if positions is None else positions,
            length=_length_repr(self.length),
            check_order=self.check_order and Omit,
        )

    def equals(self, other: Any) -> bool:  # noqa: C901
        if not isinstance(other, self.expected_type):
            return False

        if not _length_correct(self.length, other):
            return False

        if self.check_order:
            if self.positions is None:
                if self.length is None:
                    return list(self.items) == list(other)
                else:
                    return list(self.items) == list(other[: len(self.items)])
            else:
                return all(v == other[k] for k, v in self.positions.items())
        else:
            # order insensitive comparison
            # if we haven't checked length yet, check it now
            if self.length is None and len(other) != len(self.items):
                return False

            other_copy = list(other)
            for item in self.items:
                try:
                    other_copy.remove(item)
                except ValueError:
                    return False
            return True


class IsList(IsListOrTuple[List[Any]]):
    expected_type = list


class IsTuple(IsListOrTuple[Tuple[Any, ...]]):
    expected_type = tuple


def _length_repr(length: 'LengthType') -> Any:
    if length is None:
        return Omit
    elif isinstance(length, int):
        return length
    else:
        if len(length) != 2:
            raise TypeError(f'length must be a tuple of length 2, not {len(length)}')
        max_value = length[1] if isinstance(length[1], int) else plain_repr('...')
        return length[0], max_value


def _length_correct(length: 'LengthType', other: 'Sized') -> bool:
    if isinstance(length, int):
        if len(other) != length:
            return False
    elif isinstance(length, tuple):
        other_len = len(other)
        min_length, max_length = length
        if other_len < min_length:
            return False
        if isinstance(max_length, int) and other_len > max_length:
            return False
    return True
