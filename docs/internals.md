# Internals
## How the magic of `DirtyEquals.__eq__` works?
When you call `x == y`, Python first calls `x.__eq__(y)`. This would not help us
much, because we would have to keep an eye on order of the arguments when
comparing to `DirtyEquals` objects. But that's where were another feature of
Python comes in.

When `x.__eq__(y)` returns the `NotImplemented` object, then Python will try to
call `y.__eq__(x)`. Objects in the standard library return that value when they
don't know how to compare themselves to objects of `type(y)` (Without checking
the C source I can't be certain if this assumption holds for all classes, but it
works for all the basic ones).
In [`pathlib.PurePath`](https://github.com/python/cpython/blob/aebbd7579a421208f48dd6884b67dbd3278b71ad/Lib/pathlib.py#L751)
you can see an example how that is implemented in Python.

> By default, object implements `__eq__()` by using `is`,
> returning `NotImplemented` in the case of a false comparison:
> `True if x is y else NotImplemented`.

See the Python documentation for more information ([`object.__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__)).
