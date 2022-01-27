from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional, Tuple, Type, TypeVar, Union

from ._base import DirtyEquals

__all__ = (
    'IsNumeric',
    'IsNumber',
    'IsPositive',
    'IsNegative',
    'IsNonPositive',
    'IsNonNegative',
    'IsInt',
    'IsPositiveInt',
    'IsNegativeInt',
    'IsNonPositiveInt',
    'IsNonNegativeInt',
    'IsFloat',
    'IsPositiveFloat',
    'IsNegativeFloat',
    'IsNonPositiveFloat',
    'IsNonNegativeFloat',
)

from ._utils import Omit

AnyNumber = Union[int, float, complex, Decimal]
N = TypeVar('N', int, float, complex, Decimal, date, datetime, AnyNumber)


class IsNumeric(DirtyEquals[N]):
    types: Union[Type[N], Tuple[type, ...]] = int, float, complex, Decimal, date, datetime

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
        self.delta: Any = delta
        if self.approx is not None and (gt, lt, ge, le) != (None, None, None, None):
            raise TypeError('"approx" cannot be combined with "gt", "lt", "ge", or "le"')
        self.gt: Optional[N] = gt
        self.lt: Optional[N] = lt
        self.ge: Optional[N] = ge
        self.le: Optional[N] = le
        self.has_bounds_checks = not all(f is None for f in (approx, delta, gt, lt, ge, le))
        kwargs = {
            'approx': approx or Omit,
            'delta': delta or Omit,
            'gt': gt or Omit,
            'lt': lt or Omit,
            'ge': ge or Omit,
            'le': le or Omit,
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

    def bounds_checks(self, other: Any) -> bool:
        if self.approx is not None:
            if self.delta is None:
                if isinstance(other, datetime):
                    delta = timedelta(seconds=1)
                else:
                    delta = other / 100
            else:
                delta = self.delta
            return abs(self.approx - other) <= delta
        elif self.gt is not None and other <= self.gt:
            return False
        elif self.lt is not None and other >= self.lt:
            return False
        elif self.ge is not None and other < self.ge:
            return False
        elif self.le is not None and other > self.le:
            return False
        else:
            return True


class IsNumber(IsNumeric[AnyNumber]):
    types = int, float, complex, Decimal


Num = TypeVar('Num', int, float, complex, Decimal)


class IsApprox(IsNumber):
    def __init__(self, approx: Num, *, delta: Optional[Num] = None):
        super().__init__(approx=approx, delta=delta)


class IsPositive(IsNumber):
    def __init__(self) -> None:
        super().__init__(gt=0)


class IsNegative(IsNumber):
    def __init__(self) -> None:
        super().__init__(lt=0)


class IsNonPositive(IsNumber):
    def __init__(self) -> None:
        super().__init__(le=0)


class IsNonNegative(IsNumber):
    def __init__(self) -> None:
        super().__init__(ge=0)


class IsInt(IsNumeric[int]):
    types = int


class IsPositiveInt(IsInt):
    def __init__(self) -> None:
        super().__init__(gt=0)


class IsNegativeInt(IsInt):
    def __init__(self) -> None:
        super().__init__(lt=0)


class IsNonPositiveInt(IsInt):
    def __init__(self) -> None:
        super().__init__(le=0)


class IsNonNegativeInt(IsInt):
    def __init__(self) -> None:
        super().__init__(ge=0)


class IsFloat(IsNumeric[float]):
    types = float


class IsPositiveFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(gt=0)


class IsNegativeFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(lt=0)


class IsNonPositiveFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(le=0)


class IsNonNegativeFloat(IsFloat):
    def __init__(self) -> None:
        super().__init__(ge=0)
