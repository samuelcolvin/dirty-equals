## Boolean Logic

*dirty-equals* types can be combined based on either `&`
(and, all checks must be `True` for the combined check to be `True`) or `|`
(or, any check can be `True` for the combined check to be `True`).

Types can also be inverted using the `~` operator, this is equivalent to using `!=` instead of `==`.

Example:
```py
title="Boolean Combination of Types"
from dirty_equals import HasLen, Contains

assert ['a', 'b', 'c'] == HasLen(3) & Contains('a') #(1)!
assert ['a', 'b', 'c'] == HasLen(3) | Contains('z') #(2)!

assert ['a', 'b', 'c'] != Contains('z')
assert ['a', 'b', 'c'] == ~Contains('z')
```

1. The object on the left has to both have length 3 **and** contain `"a"`
2. The object on the left has to either have length 3 **or** contain `"z"`

## Initialised vs. Class comparison

!!! warning

    This does not work with PyPy.

*dirty-equals* allows comparison with types regardless of whether they've been initialised.

This saves users adding `()` in lots of places.

Example:

```py
title="Initialised vs. Uninitialised"
from dirty_equals import IsInt

# these two cases are the same
assert 1 == IsInt
assert 1 == IsInt()
```

!!! Note
    Types that require at least on argument when being initialised (like [`IsApprox`][dirty_equals.IsApprox])
    cannot be used like this, comparisons will just return `False`.

## `__repr__` and pytest compatibility

dirty-equals types have reasonable `__repr__` methods, which describe types and generally are a close match
of how they would be created:

```py
title="__repr__"
from dirty_equals import IsInt, IsApprox

assert repr(IsInt) == 'IsInt'
assert repr(IsInt()) == 'IsInt()'
assert repr(IsApprox(42)) == 'IsApprox(approx=42)'
```

However the repr method of types changes when an equals (`==`) operation on them returns a `True`, in this case
the `__repr__` method will return `repr(other)`.

```py
title="repr() after comparison"
from dirty_equals import IsInt

v = IsInt()
assert 42 == v
assert repr(v) == '42'
```

This black magic is designed to make the output of pytest when asserts on large objects fail as simple as
possible to read.

Consider the following unit test:

```py
title="pytest error example"
from datetime import datetime
from dirty_equals import IsPositiveInt, IsNow

def test_partial_dict():
    api_response_data = {
        'id': 1, #(1)!
        'first_name': 'John',
        'last_name': 'Doe',
        'created_at': datetime.now().isoformat(),
        'phone': '+44 123456789',
    }

    assert api_response_data == {
        'id': IsPositiveInt(),
        'first_name': 'John',
        'last_name': 'Doe',
        'created_at': IsNow(iso_string=True),
        # phone number is missing, so the test will fail
    }
```

1. For simplicity we've hardcoded `id` here, but in a test it could be any positive int,
   hence why we need `IsPositiveInt()`

Here's an except from the output of `pytest -vv` show the error details:

```txt title="pytest output"
E         Common items:
E         {'created_at': '2022-02-25T15:41:38.493512',
E          'first_name': 'John',
E          'id': 1,
E          'last_name': 'Doe'}
E         Left contains 1 more item:
E         {'phone': '+44 123456789'}
E         Full diff:
E           {
E            'created_at': '2022-02-25T15:41:38.493512',
E            'first_name': 'John',
E            'id': 1,
E            'last_name': 'Doe',
E         +  'phone': '+44 123456789',
E           }
```

It's easy to see that the `phone` key is missing, `id` and `created_at` are represented by the exact
values they were compared to, so don't show as different in the "Full diff" section.

!!! Warning
    This black magic only works when using initialised types, if `IsPositiveInt` was used instead `IsPositiveInt()`
    in the above example, the output would not be as clean.
