<p align="center">
  <a href="https://dirty-equals.helpmanual.io">
    <img src="https://dirty-equals.helpmanual.io/img/logo-text.svg" alt="dirty-equals">
  </a>
</p>
<p align="center">
  <em>Doing dirty (but extremely useful) things with equals.</em>
</p>
<p align="center">
  <a href="https://github.com/samuelcolvin/dirty-equals/actions?query=event%3Apush+branch%3Amain+workflow%3ACI">
    <img src="https://github.com/samuelcolvin/dirty-equals/workflows/CI/badge.svg?event=push" alt="CI">
  </a>
  <a href="https://codecov.io/gh/samuelcolvin/dirty-equals">
    <img src="https://codecov.io/gh/samuelcolvin/dirty-equals/branch/main/graph/badge.svg" alt="Coverage">
  </a>
  <a href="https://pypi.python.org/pypi/dirty-equals">
    <img src="https://img.shields.io/pypi/v/dirty-equals.svg" alt="pypi">
  </a>
  <a href="https://github.com/samuelcolvin/dirty-equals">
    <img src="https://img.shields.io/pypi/pyversions/dirty-equals.svg" alt="versions">
  </a>
  <a href="https://github.com/samuelcolvin/dirty-equals/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/samuelcolvin/dirty-equals.svg" alt="license">
  </a>
</p>

---

**Documentation**: [dirty-equals.helpmanual.io](https://dirty-equals.helpmanual.io)

**Source Code**: [github.com/samuelcolvin/dirty-equals](https://github.com/samuelcolvin/dirty-equals)

---

**dirty-equals** is a python library that (mis)uses the `__eq__` method to make python code (generally unit tests)
more declarative and therefore easier to read and write.

*dirty-equals* can be used in whatever context you like, but it comes into its own when writing unit tests for
applications where you're commonly checking the response to API calls and the contents of a database.

## Usage

Here's a trivial example of what *dirty-equals* can do:

```py
from dirty_equals import IsPositive

assert 1 == IsPositive
assert -2 == IsPositive  # this will fail!
```

**That doesn't look very useful yet!**, but consider the following unit test code using *dirty-equals*:

```py title="More Powerful Usage"
from dirty_equals import IsJson, IsNow, IsPositiveInt, IsStr

...

# user_data is a dict returned from a database or API which we want to test
assert user_data == {
    # we want to check that id is a positive int
    'id': IsPositiveInt,
    # we know avatar_file should be a string, but we need a regex as we don't know whole value
    'avatar_file': IsStr(regex=r'/[a-z0-9\-]{10}/example\.png'),
    # settings_json is JSON, but it's more robust to compare the value it encodes, not strings
    'settings_json': IsJson({'theme': 'dark', 'language': 'en'}),
    # created_ts is datetime, we don't know the exact value, but we know it should be close to now
    'created_ts': IsNow(delta=3),
}
```

Without *dirty-equals*, you'd have to compare individual fields and/or modify some fields before comparison -
the test would not be declarative or as clear.

*dirty-equals* can do so much more than that, for example:

* [`IsPartialDict`](https://dirty-equals.helpmanual.io/types/dict/#dirty_equals.IsPartialDict) 
  lets you compare a subset of a dictionary
* [`IsStrictDict`](https://dirty-equals.helpmanual.io/types/dict/#dirty_equals.IsStrictDict) 
  lets you confirm order in a dictionary
* [`IsList`](https://dirty-equals.helpmanual.io/types/sequence/#dirty_equals.IsList) and 
  [`IsTuple`](https://dirty-equals.helpmanual.io/types/sequence/#dirty_equals.IsTuple)
  lets you compare partial lists and tuples, with or without order constraints
* nesting any of these types inside any others
* [`IsInstance`](https://dirty-equals.helpmanual.io/types/other/#dirty_equals.IsInstance) 
  lets you simply confirm the type of an object
* You can even use [boolean operators](https://dirty-equals.helpmanual.io/usage/#boolean-logic) 
  `|` and `&` to combine multiple conditions
* and much more...

## Installation

Simply:

```bash
pip install dirty-equals
```

**dirty-equals** requires **Python 3.7+**.

## Internals
### How is is the magical `DirtyEquals.__eq__` called?
When you call `x == y`, Python first calls `x.__eq__(y)`. This would not help us much, because we would have to keep an eye on order of the arguments when comparing to `DirtyEquals` objects. But that's where were another feature of Python comes in.

When `x.__eq__(y)` returns the `NotImplemented` object, then Python will try to call `y.__eq__(x)`. Objects in the standard library return that value when they don't know how to compare themselves to objects of `type(y)` (Without checking the C source I can't be certain if this assumption holds for all classes, but it works for all the basic ones). In [pathlib.PurePath](https://github.com/python/cpython/blob/aebbd7579a421208f48dd6884b67dbd3278b71ad/Lib/pathlib.py#L751) you can see an example how that is implemented in Python.

> By default, object implements eq() by using is, returning NotImplemented in the case of a false comparison: True if x is y else NotImplemented.

See the Python documentation for more information ([object.__eq__](https://docs.python.org/3/reference/datamodel.html#object.__eq__])).
