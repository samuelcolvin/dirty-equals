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

{{ version }}

**dirty-equals** is a python library that (mis)uses the `__eq__` method to make python code (generally unit tests)
more declarative and therefore easier to read and write.

*dirty-equals* can be used in whatever context you like, but it comes into its own when writing unit tests for
applications where you're commonly checking the response to API calls and the contents of a database.

## Usage

Here's a trivial example of what *dirty-equals* can do:

```{.py title="Trival Usage" test="false"}
from dirty_equals import IsPositive

assert 1 == IsPositive #(1)!
assert -2 == IsPositive  # this will fail! (2)
```

1. This `assert` will pass since `1` is indeed positive, so the result of `1 == IsPositive` is `True`.
2. This will fail (raise a `AssertionError`) since `-2` is not positive,
   so the result of `-2 == IsPositive` is `False`.

**Not that interesting yet!**, but consider the following unit test code using **dirty-equals**:

```py
title="More Powerful Usage"
from dirty_equals import IsJson, IsNow, IsPositiveInt, IsStr

def test_user_endpoint(client: 'HttpClient', db_conn: 'Database'):
   client.pust('/users/create/', data=...)

   user_data = db_conn.fetchrow('select * from users')
   assert user_data == {
       'id': IsPositiveInt, #(1)!
       'username': 'samuelcolvin', #(2)!
       'avatar_file': IsStr(regex=r'/[a-z0-9\-]{10}/example\.png'), #(3)!
       'settings_json': IsJson({'theme': 'dark', 'language': 'en'}), #(4)!
       'created_ts': IsNow(delta=3), #(5)!
   }
```

1. We don't actually care what the `id` is, just that it's present, it's an `int` and it's positive.
2. We can use a normal key and value here since we know exactly what value `username` should have before we test it.
3. `avatar_file` is a string, but we don't know all of the string before the `assert`,
   just the format (regex) it should match.
4. `settings_json` is a `JSON` string, but it's simpler and more robust to confirm it represents a particular python
   object rather than compare strings.
5. `created_at` is a `datetime`, although we don't know (or care) about its exact value;
   since the user was just created we know it must be close to now. `delta` is optional, it defaults to 2 seconds.

Without **dirty-equals**, you'd have to compare individual fields and/or modify some fields before comparison
- the test would not be declarative or as clear.

**dirty-equals** can do so much more than that, for example:

* [`IsPartialDict`][dirty_equals.IsPartialDict] lets you compare a subset of a dictionary
* [`IsStrictDict`][dirty_equals.IsStrictDict] lets you confirm order in a dictionary
* [`IsList`][dirty_equals.IsList] and [`IsTuple`][dirty_equals.IsTuple] lets you compare partial lists and tuples,
  with or without order constraints
* nesting any of these types inside any others
* [`IsInstance`][dirty_equals.IsInstance] lets you simply confirm the type of an object
* You can even use [boolean operators](./usage.md#boolean-logic) `|` and `&` to combine multiple conditions
* and much more...

## Installation

Simply:

```bash
pip install dirty-equals
```

**dirty-equals** requires **Python 3.7+**.
