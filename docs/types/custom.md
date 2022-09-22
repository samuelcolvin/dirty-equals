# Custom Types

::: dirty_equals._base.DirtyEquals
    rendering:
      merge_init_into_class: false

## Custom Type Example

To demonstrate the use of custom types, we'll create a custom type that matches any even number.

We won't inherit from [`IsNumeric`][dirty_equals.IsNumeric] in this case to keep the example simple.

```py
title="IsEven"
from decimal import Decimal
from typing import Any, Union
from dirty_equals import IsOneOf
from dirty_equals import DirtyEquals

class IsEven(DirtyEquals[Union[int, float, Decimal]]):
    def equals(self, other: Any) -> bool:
        return other % 2 == 0

assert 2 == IsEven
assert 3 != IsEven
assert 'foobar' != IsEven
assert 3 == IsEven | IsOneOf(3)
```

There are a few advantages of inheriting from [`DirtyEquals`][dirty_equals.DirtyEquals] compared to just
implementing your own class with an `__eq__` method:

1. `TypeError` and `ValueError` in `equals` are caught and result in a not-equals result.
2. A useful `__repr__` is generated, and modified if the `==` operation returns `True`,
   see [pytest compatibility](../usage.md#__repr__-and-pytest-compatibility)
3. [boolean logic](../usage.md#boolean-logic) works out of the box
4. [Uninitialised usage](../usage.md#initialised-vs-class-comparison)
   (`IsEven` rather than `IsEven()`) works out of the box
