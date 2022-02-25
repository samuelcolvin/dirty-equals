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

*dirty-equals* allows comparison with types regardless of whether they've been initialised.

This saves users adding `()` in lots of places.

Example:

```py title="Initialised vs. Uninitialised"
from dirty_equals import IsInt

# these two cases are the same
assert 1 == IsInt
assert 1 == IsInt()
```

## `__repr__` and pytest compatibility

TODO.
