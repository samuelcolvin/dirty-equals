from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional, Tuple, Type, TypeVar, Union

from ._base import DirtyEquals

__all__ = (
    'IsApprox',
    'IsNumeric',
    'IsNumber',
    'IsPositive',
    'IsNegative',
    'IsNonPositive',
    'IsNonNegative',
    'IsInt',
    'IsPositiveInt',
    'IsNegativeInt',
    'IsFloat',
    'IsPositiveFloat',
    'IsNegativeFloat',
)

from ._utils import Omit

AnyNumber = Union[int, float, Decimal]
N = TypeVar('N', int, float, Decimal, date, datetime, AnyNumber)


class IsNumeric(DirtyEquals[N]):
    types: Union[Type[N], Tuple[type, ...]] = (int, float, Decimal, date, datetime)

    def __init__(
        self,
        *,
        approx: Optional[N] = None,
        delta: Optional[N] = None,
        gt: Optional[N] = None,
        lt: Optional[N] = None,
        ge: Optional[N] = None,
        le: Optional[N] = None,
    ):
        self.approx: Optional[N] = approx
        self.delta: Optional[N] = delta
        if self.approx is not None and (gt, lt, ge, le) != (None, None, None, None):
            raise TypeError('"approx" cannot be combined with "gt", "lt", "ge", or "le"')
        self.gt: Optional[N] = gt
        self.lt: Optional[N] = lt
        self.ge: Optional[N] = ge
        self.le: Optional[N] = le
        self.has_bounds_checks = not all(f is None for f in (approx, delta, gt, lt, ge, le))
        kwargs = {
            'approx': Omit if approx is None else approx,
            'delta': Omit if delta is None else delta,
            'gt': Omit if gt is None else gt,
            'lt': Omit if lt is None else lt,
            'ge': Omit if ge is None else ge,
            'le': Omit if le is None else le,
        }
        super().__init__(**kwargs)

    def prepare(self, other: Any) -> N:
        if other is True or other is False:
            raise TypeError('booleans are not numbers')
        elif not isinstance(other, self.types):
            raise TypeError(f'not a {self.types}')
        else:
            return other

    def equals(self, other: Any) -> bool:
        other = self.prepare(other)

        if self.has_bounds_checks:
            return self.bounds_checks(other)
        else:
            return True

    def bounds_checks(self, other: N) -> bool:
        if self.approx is not None:
            if self.delta is None:
                if isinstance(other, date):
                    delta: Any = timedelta(seconds=1)
                else:
                    delta = other / 100
            else:
                delta = self.delta
            return self.approx_equals(other, delta)
        elif self.gt is not None and not other > self.gt:
            return False
        elif self.lt is not None and not other < self.lt:
            return False
        elif self.ge is not None and not other >= self.ge:
            return False
        elif self.le is not None and not other <= self.le:
            return False
        else:
            return True

    def approx_equals(self, other: Any, delta: Any) -> bool:
        return abs(self.approx - other) <= delta


class IsNumber(IsNumeric[AnyNumber]):
    types = int, float, Decimal


Num = TypeVar('Num', int, float, Decimal)


class IsApprox(IsNumber):
    def __init__(self, approx: Num, *, delta: Optional[Num] = None):
        super().__init__(approx=approx, delta=delta)


class IsPositive(IsNumber):
    def __init__(self) -> None:
        super().__init__(gt=0)
        self._repr_kwargs = {}


class IsNegative(IsNumber):
    def __init__(self) -> None:
        super().__init__(lt=0)
        self._repr_kwargs = {}


class IsNonPositive(IsNumber):
    def __init__(self) -> None:
        super().__init__(le=0)
        self._repr_kwargs = {}


class IsNonNegative(IsNumber):
    def __init__(self) -> None:
        super().__init__(ge=0)
        self._repr_kwargs = {}


class IsInt(IsNumeric[int]):
    types = int


class IsPositiveInt(IsInt):
    def __init__(self) -> None:
        super().__init__(gt=0)
        self._repr_kwargs = {}


class IsNegativeInt(IsInt):
    def __init__(self) -> None:
        super().__init__(lt=0)
        self._repr_kwargs = {}


class IsFloat(IsNumeric[float]):
    types = float


class IsPositiveFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(gt=0)
        self._repr_kwargs = {}


class IsNegativeFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(lt=0)
        self._repr_kwargs = {}
