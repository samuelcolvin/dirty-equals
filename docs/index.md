<p align="center">
  <img src="/img/logo-text.svg" alt="dirty-equals">
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

**dirty-equals** is a python library that (mis)uses the `__eq__` method to make python code (generally unit tests)
more declarative and therefore easier to read and write.

## Usage

Here's a trivial example of what *dirty-equals* can do:

```py title="Trival Usage"
from dirty_equals import IsPositive

assert 1 == IsPositive #(1)!
assert -2 == IsPositive  #(2)!
```

1. This `assert` will pass since `1` is indeed positive, so the result of `1 == IsPositive` is `True`.
2. This will fail (raise a `AssertionError`) since `-2` is not positive, 
   so the result of `-2 == IsPositive` is `False`.

That doesn't look very useful yet, but consider the following unit test code using **dirty-equals**:

```py title="More Powerful Usage"
from dirty_equals import IsJson, IsNow, IsPositiveInt, IsStr

...

# user_data is a dict returned from a database or API which we want to test
assert user_data == {
    'id': IsPositiveInt, #(1)!
    'avatar_file': IsStr(regex=r'/[a-z0-9\-]{10}/example\.png'), #(2)!
    'settings_json': IsJson({'theme': 'dark', 'language': 'en'}), #(3)!
    'created_ts': IsNow(delta=3), #(4)!
}
```

1. We don't actually care what the `id` is, just that it's present, it's an `int` and it's a positive.
2. `avatar_file` is a string, but we don't know all of it, just the format (regex) it should match.
3. `settings_json` is a `JSON` string, but it's simpler and more robust to confirm it represents a particular python
   object rather than compare strings.
4. `created_at` is a `datetime`, although we don't know (or care) about its exact value;
   since the user was just created we know it must be close to now. `delta` is optional, it defaults to 2 seconds.


Without **dirty-equals**, you'd have to compare individual fields and/or modify some fields before comparison 
- the test would not be declarative or as clear.

**dirty-equals** can do so much more than that, for example:

* `PartialDict` let's you compare a subset of a dictionary
* `IsStrictDict` let's you confirm order in a dictionary
* `IsList` and `IsTuple` lets you compare partial lists and tuples, with or without order constraints
* `IsInstance` lets you simply confirm the type of an object
* You can even use boolean operators `|` and `&` to combine multiple conditions
* and much more...

## Installation

Simply:

```bash
pip install dirty-equals
```

**dirty-equals** requires **Python 3.7+**.
