from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, TypeVar, Union, overload

from ._base import DirtyEquals
from ._utils import Omit

if TYPE_CHECKING:
    from typing import TypeAlias

__all__ = 'IsListOrTuple', 'IsList', 'IsTuple'
T = TypeVar('T', List[Any], Tuple[Any, ...])
# "Any" here as a hack because there's no type for Ellipsis
ExpectedLengthType: 'TypeAlias' = 'Union[None, int, Union[int, Union[int, Any]]]'


class IsListOrTuple(DirtyEquals[T]):
    expected_type: Union[Type[Any], Tuple[Type[Any], Type[Any]]] = (list, tuple)

    @overload
    def __init__(self, *items: Any, check_order: bool = True, length: 'ExpectedLengthType' = None):
        ...

    @overload
    def __init__(self, positions: Dict[int, Any], length: 'ExpectedLengthType' = None):
        ...

    def __init__(
        self,
        *items: Any,
        positions: Optional[Dict[int, Any]] = None,
        check_order: bool = True,
        length: 'ExpectedLengthType' = None,
    ) -> None:
        length_repr = Omit if length is None else length
        if positions is not None:
            self.positions: Optional[Dict[int, Any]] = positions
            if items:
                raise TypeError(f'{self.__class__.__name__} requires either args or positions, not both')
            if not check_order:
                raise TypeError('check_order=False is not compatible with positions')
            super().__init__(positions=positions, length=length_repr)
        else:
            self.positions = None
            self.items = items
            super().__init__(*items, length=length_repr)
        self.length = length
        self.check_order = check_order

    def equals(self, other: Any) -> bool:
        if not isinstance(other, self.expected_type):
            return False

        if isinstance(self.length, int):
            if len(other) != self.length:
                return False
        elif isinstance(self.length, tuple):
            other_len = len(other)
            if other_len < self.length[0]:
                return False
            max_len = self.length[1]
            if max_len is not Ellipsis and other_len > max_len:
                return False

        if self.check_order:
            if self.positions is None:
                return list(self.items) == list(other[: len(self.items)])
            else:
                return all(v == other[k] for k, v in self.positions.items())
        else:
            # order insensitive comparison
            # if we haven't checked length yet, check it now
            if self.length is None and len(other) != len(self.items):
                return False

            return all(item in other for item in self.items)


class IsList(IsListOrTuple[List[Any]]):
    expected_type = list


class IsTuple(IsListOrTuple[Tuple[Any, ...]]):
    expected_type = tuple
