from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sized, Tuple, Type, TypeVar, Union, overload

from ._base import DirtyEquals
from ._utils import Omit, plain_repr

if TYPE_CHECKING:
    from typing import TypeAlias

__all__ = 'HasLen', 'IsListOrTuple', 'IsList', 'IsTuple'
T = TypeVar('T', List[Any], Tuple[Any, ...])
LengthType: 'TypeAlias' = 'Union[None, int, Tuple[int, Union[int, Any]]]'


class HasLen(DirtyEquals[Sized]):
    """
    Check that some has a given length, or length in a given range.
    """

    @overload
    def __init__(self, length: int):
        ...

    @overload
    def __init__(self, min_length: int, max_length: Union[int, Any]):
        ...

    def __init__(self, min_length: int, max_length: Union[None, int, Any] = None):  # type: ignore[misc]
        """
        Args:
            min_length: Expected length if `max_length` is not given, else minimum length.
            max_length: Expected maximum length, use an ellipsis `...` to indicate that there's no maximum.

        ```py title="HasLen"
        from dirty_equals import HasLen

        assert [1, 2, 3] == HasLen(3) # (1)!
        assert '123' == HasLen(3, ...) # (2)!
        assert (1, 2, 3) == HasLen(3, 5) # (3)!
        assert (1, 2, 3) == HasLen(0, ...) # (4)!
        ```

        1. Length must be 3.
        2. Length must be 3 or higher.
        3. Length must be between 3 and 5 inclusive.
        4. Length is required but can take any value.
        """
        if max_length is None:
            self.length: 'LengthType' = min_length
            super().__init__(self.length)
        else:
            self.length = (min_length, max_length)
            super().__init__(*_length_repr(self.length))

    def equals(self, other: Any) -> bool:
        return _length_correct(self.length, other)


class IsListOrTuple(DirtyEquals[T]):
    """
    Check that some object is a list or tuple and optionally its values match some constraints.
    """

    allowed_type: Union[Type[T], Tuple[Type[List[Any]], Type[Tuple[Any, ...]]]] = (list, tuple)

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
    ):
        """
        `IsListOrTuple` and its subclasses can be initialised in two ways:

        Args:
            *items: Positional members of an object to check. These must start from the zeroth position, but
                (depending on the value of `length`) may not include all values of the list/tuple being checked.
            check_order: Whether to enforce the order of the items.
            length (Union[int, Tuple[int, Union[int, Any]]]): length constraints, int or tuple matching the arguments
                of [`HasLen`][dirty_equals.HasLen].

        or,

        Args:
            positions (Dict[int, Any]): Instead of `*items`, a dictionary of positions and
                values to check and be provided.
            length (Union[int, Tuple[int, Union[int, Any]]]): length constraints, int or tuple matching the arguments
                of [`HasLen`][dirty_equals.HasLen].

        ```py title="IsListOrTuple"
        from dirty_equals import IsListOrTuple

        assert [1, 2, 3] == IsListOrTuple(1, 2, 3)
        assert (1, 3, 2) == IsListOrTuple(1, 2, 3, check_order=False)
        assert [{'a': 1}, {'a': 2}] == (
            IsListOrTuple({'a': 2}, {'a': 1}, check_order=False) # (1)!
        )
        assert [1, 2, 3, 3] == IsListOrTuple(1, 2, 3, check_order=False) # (2)!

        assert [1, 2, 3, 4, 5] == IsListOrTuple(1, 2, 3, length=...) # (3)!
        assert [1, 2, 3, 4, 5] != IsListOrTuple(1, 2, 3, length=(8, 10)) # (4)!

        assert ['a', 'b', 'c', 'd'] == (
            IsListOrTuple(positions={2: 'c', 3: 'd'}) # (5)!
        )
        assert ['a', 'b', 'c', 'd'] == (
            IsListOrTuple(positions={2: 'c', 3: 'd'}, length=4) # (6)!
        )

        assert [1, 2, 3, 4] == IsListOrTuple(3, check_order=False, length=(0, ...)) # (7)!
        ```

        1. Unlike using sets for comparison, we can do order-insensitive comparisons on objects that are not hashable.
        2. And we won't get caught out be duplicate values
        3. Here we're just checking the first 3 items, the compared list or tuple can be of any length
        4. Compared list is not long enough
        5. Compare using `positions`, here no length if enforced
        6. Compare using `positions` but with a length constraint
        7. Here we're just confirming that the value `3` is in the list.
        """
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
        if not isinstance(other, self.allowed_type):
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
    """
    All the same functionality as [`IsListOrTuple`][dirty_equals.IsListOrTuple], but the compared value must be a list.

    ```py title="IsList"
    from dirty_equals import IsList

    assert [1, 2, 3] == IsList(1, 2, 3)
    assert [1, 2, 3] == IsList(positions={2: 3})
    assert [1, 2, 3] == IsList(1, 2, 3, check_order=False)

    assert (1, 2, 3) != IsList(1, 2, 3)
    ```
    """

    allowed_type = list


class IsTuple(IsListOrTuple[Tuple[Any, ...]]):
    """
    All the same functionality as [`IsListOrTuple`][dirty_equals.IsListOrTuple], but the compared value must be a tuple.

    ```py title="IsTuple"
    from dirty_equals import IsTuple

    assert (1, 2, 3) == IsTuple(1, 2, 3)
    assert (1, 2, 3) == IsTuple(positions={2: 3})
    assert (1, 2, 3) == IsTupleOrTuple(1, 2, 3, check_order=False)

    assert [1, 2, 3] != IsTuple(1, 2, 3)
    ```
    """

    allowed_type = tuple


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
