from abc import ABCMeta
from typing import Any, Dict, Generic, Iterable, Optional, TypeVar, Union

from ._utils import Omit

__all__ = 'DirtyEquals', 'IsInstanceOf'


class DirtyEqualsMeta(ABCMeta):
    def _get_instance(self) -> 'DirtyEquals[Any]':
        try:
            return self()
        except TypeError as e:
            raise TypeError(f'{self.__name__} cannot be used without initialising') from e

    def __eq__(self, other: Any) -> bool:
        # this is required as fancy things happen when creating generics
        if self is DirtyEquals:
            return False
        else:
            return self._get_instance() == other

    def __or__(self, other: Any) -> 'DirtyOr':
        return self._get_instance() | other

    def __and__(self, other: Any) -> 'DirtyAnd':
        return self._get_instance() & other

    def __invert__(self) -> 'DirtyNot':
        return ~self._get_instance()

    def __repr__(self) -> str:
        return f'{self.__name__}()'


T = TypeVar('T')


class DirtyEquals(Generic[T], metaclass=DirtyEqualsMeta):
    __slots__ = '_other', '_was_equal', '_repr_args', '_repr_kwargs'

    def __init__(self, *repr_args: Any, **repr_kwargs: Any) -> None:
        self._other: Any = None
        self._was_equal: Optional[bool] = None
        self._repr_args: Iterable[Any] = repr_args
        self._repr_kwargs: Dict[str, Any] = repr_kwargs

    def equals(self, other: Any) -> bool:
        raise NotImplementedError()

    @property
    def value(self) -> T:
        if self._was_equal:
            return self._other
        else:
            raise RuntimeError('value is not available until __eq__ has been called')

    def __eq__(self, other: Any) -> bool:
        self._other = other
        try:
            self._was_equal = self.equals(other)
        except (TypeError, ValueError):
            self._was_equal = False

        return self._was_equal

    def __or__(self, other: Any) -> 'DirtyOr':
        return DirtyOr(self, other)

    def __and__(self, other: Any) -> 'DirtyAnd':
        return DirtyAnd(self, other)

    def __invert__(self) -> 'DirtyNot':
        return DirtyNot(self)

    def __repr__(self) -> str:
        if self._was_equal:
            # if we've got the correct value return it to aid in diffs
            return repr(self._other)
        else:
            # else return something which explains what's going on.
            args = [repr(arg) for arg in self._repr_args if arg is not Omit]
            args += [f'{k}={v!r}' for k, v in self._repr_kwargs.items() if v is not Omit]
            return f'{self.__class__.__name__}({", ".join(args)})'


class DirtyOr(DirtyEquals[Any]):
    def __init__(self, a: DirtyEquals[Any], b: DirtyEquals[Any]):
        self.a = a
        self.b = b
        super().__init__()

    def equals(self, other: Any) -> bool:
        return self.a == other or self.b == other


class DirtyAnd(DirtyEquals[Any]):
    def __init__(self, a: DirtyEquals[Any], b: DirtyEquals[Any]):
        self.a = a
        self.b = b
        super().__init__()

    def equals(self, other: Any) -> bool:
        return self.a == other and self.b == other


class DirtyNot(DirtyEquals[Any]):
    def __init__(self, subject: DirtyEquals[Any]):
        self.subject = subject
        super().__init__()

    def equals(self, other: Any) -> bool:
        return self.subject != other


ExpectedType = TypeVar('ExpectedType', bound=Union[type, tuple[Union[type, tuple[Any, ...]], ...]])


class IsInstanceOfMeta(DirtyEqualsMeta):
    def __getitem__(self, item: ExpectedType) -> 'IsInstanceOf[ExpectedType]':
        return IsInstanceOf(item)


class IsInstanceOf(DirtyEquals[ExpectedType], metaclass=IsInstanceOfMeta):
    def __init__(self, expected_type: ExpectedType, only_direct_subclass: bool = False) -> None:
        self.expected_type = expected_type
        self.only_direct_subclass = only_direct_subclass
        super().__init__()

    def equals(self, other: Any) -> bool:
        if self.only_direct_subclass:
            return type(other) == self.expected_type
        else:
            return isinstance(other, self.expected_type)
