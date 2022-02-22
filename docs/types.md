## Numeric Types

### `IsInt`

Checks that a value is an integer, but not a bool (`True` or `False`) or a float.

```py title="IsInt"
from dirty_equals import IsInt

assert 1 == IsInt
assert -2 == IsInt
assert 1.0 != IsInt
assert 'foobar' != IsInt
assert True != IsInt #(1)!
```

1. This might not be what you expect since `instance(True, int)` is `True` but to me, it doesn't make sense for booleans
   to be allowed as integers in general.

### `IsFloat`

Checks that a value is a float.

```py title="IsFloat"
from dirty_equals import IsFloat

assert 1.0 == IsFloat
assert 1 != IsFloat
```

### `IsPositive`

Check that a value is positive (`> 0`), can be an `int`, a `float` or a `Decimal` 
(or indeed any value which implements `__gt__` for `0`).

```py title="IsPositive"
from decimal import Decimal
from dirty_equals import IsPositive

assert 1.0 == IsPositive
assert 1 == IsPositive
assert Decimal('3.14') == IsPositive
assert 0 != IsPositive
assert -1 != IsPositive
```

### `IsNegative`

Check that a value is negative (`< 0`), can be an `int`, a `float` or a `Decimal` 
(or indeed any value which implements `__lt__` for `0`).

```py title="IsNegative"
from decimal import Decimal
from dirty_equals import IsNegative

assert -1.0 == IsNegative
assert -1 == IsNegative
assert Decimal('-3.14') == IsNegative
assert 0 != IsNegative
assert 1 != IsNegative
```

### `IsNonNegative`

Check that a value is positive or zero (`>= 0`), can be an `int`, a `float` or a `Decimal` 
(or indeed any value which implements `__ge__` for `0`).

```py title="IsNonNegative"
from decimal import Decimal
from dirty_equals import IsNonNegative

assert 1.0 == IsNonNegative
assert 1 == IsNonNegative
assert Decimal('3.14') == IsNonNegative
assert 0 == IsNonNegative
assert -1 != IsNonNegative
assert Decimal('0') == IsNonPositive
```

### `IsNonPositive`

Check that a value is negative or zero (`<=0`), can be an `int`, a `float` or a `Decimal` 
(or indeed any value which implements `__le__` for `0`).

```py title="IsNonPositive"
from decimal import Decimal
from dirty_equals import IsNonPositive

assert -1.0 == IsNonPositive
assert -1 == IsNonPositive
assert Decimal('-3.14') == IsNonPositive
assert 0 == IsNonPositive
assert 1 != IsNonPositive
assert Decimal('-0') == IsNonPositive
assert Decimal('0') == IsNonPositive
```

### `IsPositiveInt`

Like [`IsPositive`](#ispositive) but only for `int`s.

```py title="IsPositiveInt"
from decimal import Decimal
from dirty_equals import IsPositiveInt

assert 1 == IsPositiveInt
assert 1.0 != IsPositiveInt
assert Decimal('3.14') != IsPositiveInt
assert 0 != IsPositiveInt
assert -1 != IsPositiveInt
```

### `IsNegativeInt`

Like [`IsNegative`](#isnegative) but only for `int`s.

```py title="IsNegativeInt"
from decimal import Decimal
from dirty_equals import IsNegativeInt

assert -1 == IsNegativeInt
assert -1.0 != IsNegativeInt
assert Decimal('-3.14') != IsNegativeInt
assert 0 != IsNegativeInt
assert 1 != IsNegativeInt
```

### `IsPositiveFloat`


Like [`IsPositive`](#ispositive) but only for `float`s.

```py title="IsPositiveFloat"
from decimal import Decimal
from dirty_equals import IsPositiveFloat

assert 1.0 == IsPositiveFloat
assert 1 != IsPositiveFloat
assert Decimal('3.14') != IsPositiveFloat
assert 0.0 != IsPositiveFloat
assert -1.0 != IsPositiveFloat
```

### `IsNegativeFloat`

Like [`IsNegative`](#isnegative) but only for `float`s.

```py title="IsNegativeFloat"
from decimal import Decimal
from dirty_equals import IsNegativeFloat

assert -1.0 == IsNegativeFloat
assert -1 != IsNegativeFloat
assert Decimal('-3.14') != IsNegativeFloat
assert 0.0 != IsNegativeFloat
assert 1.0 != IsNegativeFloat
```

### `IsApprox`

### `IsNumber`

### `IsNumeric`

## Date and Time Types

### `IsDatetime`

### `IsNow`

# Dictionary Types

### `IsDict`

### `IsPartialDict`

### `IsStrictDict`

## List and Tuples Types

### `HasLen`

### `IsList`

### `IsTuple`

### `IsListOrTuple`

## String Types

### `IsStr`

### `IsBytes`

### `IsAnyStr`

## Other Types

### `FunctionCheck`

### `IsInstance`

### `IsJson`

### `IsUUID`

### `AnyThing`
