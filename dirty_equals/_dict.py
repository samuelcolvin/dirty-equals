from __future__ import annotations

from typing import Any, Callable, Container, Dict, Optional, Union, overload

from dirty_equals._base import DirtyEquals


class IsDict(DirtyEquals[Dict[Any, Any]]):
    """
    Base class for comparing dictionaries. By default, `IsDict` isn't particularly useful on its own
    (it behaves pretty much like a normal `dict`), but it can be subclassed
    (see [`IsPartialDict`][dirty_equals.IsPartialDict] and [`IsStrictDict`][dirty_equals.IsStrictDict]) or modified
    with `.settings(...)` to powerful things.
    """

    @overload
    def __init__(self, expected: Dict[Any, Any]):
        ...

    @overload
    def __init__(self, **expected: Any):
        ...

    def __init__(self, *expected_args: Dict[Any, Any], **expected_kwargs: Any):
        """
        Can be created from either key word arguments or an existing dictionary (same as `dict()`).

        ```py title="IsDict"
        from dirty_equals import IsDict

        assert {'a': 1, 'b': 2} == IsDict(a=1, b=2)
        assert {1: 2, 3: 4} == IsDict({1: 2, 3: 4})
        ```
        """
        if expected_kwargs:
            self.expected_values = expected_kwargs
            if expected_args:
                raise TypeError('IsDict requires either a single argument or kwargs, not both')
        elif not expected_args:
            self.expected_values = {}
        elif len(expected_args) == 1:
            self.expected_values = expected_args[0]
        else:
            raise TypeError(f'IsDict expected at most 1 argument, got {len(expected_args)}')

        if not isinstance(self.expected_values, dict):
            raise TypeError(f'expected_values must be a dict, got {type(self.expected_values)}')

        self.strict = False
        self.partial = False
        self.ignore_values: Union[Container[Any], Callable[[Any], bool]] = {None}
        self._post_init()
        super().__init__()

    def _post_init(self) -> None:
        pass

    def settings(
        self,
        *,
        strict: Optional[bool] = None,
        partial: Optional[bool] = None,
        ignore_values: Union[None, Container[Any], Callable[[Any], bool]] = None,
    ) -> IsDict:
        """
        Allows you to customise the behaviour of `IsDict`, technically a new `IsDict` is required to allow chaining.

        Args:
            strict: If `True`, the order of key/value pairs must match.
            partial: If `True`, values are ignored if they match `ignore_values`.
            ignore_values: Values to ignore in comparison if `partial` is `True`, defaults to `{None}`. Can be either
                a set of values to ignore, or a function that takes a value and should return `True` if the value should
                be ignored.

        ```py title="IsDict.settings(...)"
        from dirty_equals import IsDict

        assert {'a': 1, 'b': 2, 'c': None} != IsDict(a=1, b=2)
        assert {'a': 1, 'b': 2, 'c': None} == IsDict(a=1, b=2).settings(partial=True) # (1)!

        assert {'b': 2, 'a': 1} == IsDict(a=1, b=2)
        assert {'b': 2, 'a': 1} != IsDict(a=1, b=2).settings(strict=True) # (2)!

        # combining partial and strict
        assert {'a': 1, 'b': 2, 'c': 3} == IsDict(a=1, c=3).settings(strict=True, partial=True)
        assert {'b': 2, 'c': 3, 'a': 1} != IsDict(a=1, c=3).settings(strict=True, partial=True)
        ```

        1. This is the same as [`IsPartialDict(a=1, b=2)`][dirty_equals.IsPartialDict]
        2. This is the same as [`IsStrictDict(a=1, b=2)`][dirty_equals.IsStrictDict]
        """
        new_cls = self.__class__(self.expected_values)
        new_cls.__dict__ = self.__dict__.copy()
        if strict is not None:
            new_cls.strict = strict
        if partial is not None:
            new_cls.partial = partial
        if ignore_values is not None:
            new_cls.ignore_values = ignore_values
        return new_cls

    def equals(self, other: Dict[Any, Any]) -> bool:
        if not isinstance(other, dict):
            return False

        if self.partial:
            expected = self._filter_dict(self.expected_values)
            other = self._filter_dict(other)
        else:
            expected = self.expected_values

        if other != expected:
            return False

        if self.strict and list(other.keys()) != list(expected.keys()):
            return False

        return True

    def _filter_dict(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        return {k: v for k, v in d.items() if not self._ignore_value(v)}

    def _ignore_value(self, v: Any) -> bool:
        if callable(self.ignore_values):
            return self.ignore_values(v)
        else:
            return v in self.ignore_values

    def _repr_ne(self) -> str:
        name = self.__class__.__name__
        modifiers = []
        if self.partial != (name == 'IsPartialDict'):
            modifiers += [f'partial={self.partial}']
        if self.partial and (self.ignore_values != {None} or name != 'IsPartialDict'):
            r = self.ignore_values.__name__ if callable(self.ignore_values) else repr(self.ignore_values)
            modifiers += [f'ignore_values={r}']
        if self.strict != (name == 'IsStrictDict'):
            modifiers += [f'strict={self.strict}']

        if modifiers:
            mod = f'[{", ".join(modifiers)}]'
        else:
            mod = ''

        args = [f'{k}={v!r}' for k, v in self.expected_values.items()]
        return f'{name}{mod}({", ".join(args)})'


class IsPartialDict(IsDict):
    """
    Partial dictionary comparison, this is the same as
    [`IsDict(...).settings(partial=True)`][dirty_equals.IsDict.settings].

    Again, `.settings(...)` can be used to customise the behaviour of `IsPartialDict`.

    ```py title="IsPartialDict"
    from dirty_equals import IsPartialDict

    assert {'a': 1, 'b': 2, 'c': None} == IsPartialDict(a=1, b=2)
    assert {'a': 1, 'b': 2, 'c': None, 'c': 'ignore'} == (
        IsPartialDict(a=1, b=2).settings(ignore_values={None, 'ignore'})
    )


    def custom_ignore(v: Any) -> bool:
        return v % 2 == 0

    assert {'a': 1, 'b': 2, 'c': 3, 'd': 4} != (
        IsPartialDict(a=1, c=3).settings(ignore_values=custom_ignore)
    )

    # combining partial and strict
    assert {'a': 1, 'b': 2, 'c': 3} == IsPartialDict(a=1, c=3).settings(strict=True)
    assert {'b': 2, 'c': 3, 'a': 1} != IsPartialDict(a=1, c=3).settings(strict=True)
    ```
    """

    def _post_init(self) -> None:
        self.partial = True


class IsStrictDict(IsDict):
    """
    Dictionary comparison with order enforced, this is the same as
    [`IsDict(...).settings(strict=True)`][dirty_equals.IsDict.settings].

    ```py title="IsDict.settings(...)"
    from dirty_equals import IsDict

    assert {'a': 1, 'b': 2} == IsStrictDict(a=1, b=2)
    assert {'a': 1, 'b': 2, 'c': 3} != IsStrictDict(a=1, b=2)
    assert {'b': 2, 'a': 1} != IsStrictDict(a=1, b=2)

    # combining partial and strict
    assert {'a': 1, 'b': 2, 'c': 3} == IsStrictDict(a=1, c=3).settings(partial=True)
    assert {'b': 2, 'c': 3, 'a': 1} != IsStrictDict(a=1, c=3).settings(partial=True)
    ```
    """

    def _post_init(self) -> None:
        self.strict = True
