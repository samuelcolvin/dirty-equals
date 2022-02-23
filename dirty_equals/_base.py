from abc import ABCMeta
from typing import TYPE_CHECKING, Any, Dict, Generic, Iterable, Optional, Tuple, TypeVar, Union

try:
    from typing import Protocol
except ImportError:
    # Python 3.7 doesn't have Protocol
    Protocol = object  # type: ignore[assignment]

from ._utils import Omit

if TYPE_CHECKING:
    from typing import TypeAlias

__all__ = 'DirtyEquals', 'IsInstance', 'AnyThing'


class DirtyEqualsMeta(ABCMeta):
    def __eq__(self, other: Any) -> bool:
        # this is required as fancy things happen when creating generics which include equals checks, without it
        # we get some recursive errors
        if self is DirtyEquals or other is Generic or other is Protocol:
            return False
        else:
            try:
                return self() == other
            except TypeError:
                # we don't want to raise a type error here since somewhere deep in pytest it does something like
                # type(a) == type(b), if we raised TypeError we would upset the pytest error message
                return False

    def __or__(self, other: Any) -> 'DirtyOr':  # type: ignore[override]
        return DirtyOr(self, other)

    def __and__(self, other: Any) -> 'DirtyAnd':
        return DirtyAnd(self, other)

    def __invert__(self) -> 'DirtyNot':
        return DirtyNot(self)

    def __hash__(self) -> int:
        return hash(self.__name__)

    def __repr__(self) -> str:
        return self.__name__


T = TypeVar('T')


class DirtyEquals(Generic[T], metaclass=DirtyEqualsMeta):
    """
    Base type for all dirty-equals types.
    """

    __slots__ = '_other', '_was_equal', '_repr_args', '_repr_kwargs'

    def __init__(self, *repr_args: Any, **repr_kwargs: Any):
        self._other: Any = None
        self._was_equal: Optional[bool] = None
        self._repr_args: Iterable[Any] = repr_args
        self._repr_kwargs: Dict[str, Any] = repr_kwargs

    def equals(self, other: Any) -> bool:
        """
        Abstract method, must be implemented by subclasses.
        """
        raise NotImplementedError()

    @property
    def value(self) -> T:
        """
        Returns the value last successfully compared to this type.
        """
        if self._was_equal:
            return self._other
        else:
            raise AttributeError('value is not available until __eq__ has been called')

    def __eq__(self, other: Any) -> bool:
        self._other = other
        try:
            self._was_equal = self.equals(other)
        except (TypeError, ValueError):
            self._was_equal = False

        return self._was_equal

    def __ne__(self, other: Any) -> bool:
        # We don't set _was_equal to avoid strange errors in pytest
        self._other = other
        try:
            return not self.equals(other)
        except (TypeError, ValueError):
            return True

    def __or__(self, other: Any) -> 'DirtyOr':
        return DirtyOr(self, other)

    def __and__(self, other: Any) -> 'DirtyAnd':
        return DirtyAnd(self, other)

    def __invert__(self) -> 'DirtyNot':
        return DirtyNot(self)

    def _repr_ne(self) -> str:
        args = [repr(arg) for arg in self._repr_args if arg is not Omit]
        args += [f'{k}={v!r}' for k, v in self._repr_kwargs.items() if v is not Omit]
        return f'{self.__class__.__name__}({", ".join(args)})'

    def __repr__(self) -> str:
        if self._was_equal:
            # if we've got the correct value return it to aid in diffs
            return repr(self._other)
        else:
            # else return something which explains what's going on.
            return self._repr_ne()


InstanceOrType: 'TypeAlias' = 'Union[DirtyEquals[Any], DirtyEqualsMeta]'


class DirtyOr(DirtyEquals[Any]):
    def __init__(self, a: 'InstanceOrType', b: 'InstanceOrType', *extra: 'InstanceOrType'):
        self.dirties = (a, b) + extra
        super().__init__()

    def equals(self, other: Any) -> bool:
        return any(d == other for d in self.dirties)

    def _repr_ne(self) -> str:
        return ' | '.join(_repr_ne(d) for d in self.dirties)


class DirtyAnd(DirtyEquals[Any]):
    def __init__(self, a: InstanceOrType, b: InstanceOrType, *extra: InstanceOrType):
        self.dirties = (a, b) + extra
        super().__init__()

    def equals(self, other: Any) -> bool:
        return all(d == other for d in self.dirties)

    def _repr_ne(self) -> str:
        return ' & '.join(_repr_ne(d) for d in self.dirties)


class DirtyNot(DirtyEquals[Any]):
    def __init__(self, subject: InstanceOrType):
        self.subject = subject
        super().__init__()

    def equals(self, other: Any) -> bool:
        return self.subject != other

    def _repr_ne(self) -> str:
        return f'~{_repr_ne(self.subject)}'


def _repr_ne(v: InstanceOrType) -> str:
    if isinstance(v, DirtyEqualsMeta):
        return repr(v)
    else:
        return v._repr_ne()


ExpectedType = TypeVar('ExpectedType', bound=Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]])


class IsInstanceMeta(DirtyEqualsMeta):
    def __getitem__(self, item: ExpectedType) -> 'IsInstance[ExpectedType]':
        return IsInstance(item)


class IsInstance(DirtyEquals[ExpectedType], metaclass=IsInstanceMeta):
    """
    A type which checks that the value is an instance of the expected type. TODO.
    """

    def __init__(self, expected_type: ExpectedType, only_direct_instance: bool = False):
        self.expected_type = expected_type
        self.only_direct_instance = only_direct_instance
        super().__init__(expected_type)

    def equals(self, other: Any) -> bool:
        if self.only_direct_instance:
            return type(other) == self.expected_type
        else:
            return isinstance(other, self.expected_type)


class AnyThing(DirtyEquals[Any]):
    """
    A type which matches any value. TODO.
    """

    def equals(self, other: Any) -> bool:
        return True
