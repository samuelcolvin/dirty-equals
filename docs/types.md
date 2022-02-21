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



```py title="IsPositive"
from dirty_equals import IsPositive

assert 1.0 == IsPositive
assert 1 == IsPositive
assert 0 == IsPositive
assert -1 == IsPositive
```

### `IsNegative`

### `IsNonPositive`

### `IsNonNegative`

### `IsPositiveInt`

### `IsNegativeInt`

### `IsPositiveFloat`

### `IsNegativeFloat`

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
