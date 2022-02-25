from __future__ import annotations

from typing import Any, Callable, Container, Dict, Optional, Union, overload

from ._base import DirtyEquals, DirtyEqualsMeta

NotGiven = object()


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

        `IsDict` is not particularly useful on its own, but it can be subclassed or modified with
        [`.settings(...)`][dirty_equals.IsDict.settings] to facilitate powerful comparison of dictionaries.

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
        self.ignore: Union[None, Container[Any], Callable[[Any], bool]] = None
        self._post_init()
        super().__init__()

    def _post_init(self) -> None:
        pass

    def settings(
        self,
        *,
        strict: Optional[bool] = None,
        partial: Optional[bool] = None,
        ignore: Union[None, Container[Any], Callable[[Any], bool]] = NotGiven,  # type: ignore[assignment]
    ) -> IsDict:
        """
        Allows you to customise the behaviour of `IsDict`, technically a new `IsDict` is required to allow chaining.

        Args:
            strict (bool): If `True`, the order of key/value pairs must match.
            partial (bool): If `True`, only keys include in the wrapped dict are checked.
            ignore (Union[None, Container[Any], Callable[[Any], bool]]): Values to omit from comparison.
                Can be either a `Container` (e.g. `set` or `list`) of values to ignore, or a function that takes a
                value and should return `True` if the value should be ignored.

        ```py title="IsDict.settings(...)"
        from dirty_equals import IsDict

        assert {'a': 1, 'b': 2, 'c': None} != IsDict(a=1, b=2)
        assert {'a': 1, 'b': 2, 'c': None} == IsDict(a=1, b=2).settings(partial=True) #(1)!

        assert {'b': 2, 'a': 1} == IsDict(a=1, b=2)
        assert {'b': 2, 'a': 1} != IsDict(a=1, b=2).settings(strict=True) #(2)!

        # combining partial and strict
        assert {'a': 1, 'b': None, 'c': 3} == IsDict(a=1, c=3).settings(strict=True, partial=True)
        assert {'b': None, 'c': 3, 'a': 1} != IsDict(a=1, c=3).settings(strict=True, partial=True)
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
        if ignore is not NotGiven:
            new_cls.ignore = ignore

        if new_cls.partial and new_cls.ignore:
            raise TypeError('partial and ignore cannot be used together')

        return new_cls

    def equals(self, other: Dict[Any, Any]) -> bool:
        if not isinstance(other, dict):
            return False

        expected = self.expected_values
        if self.partial:
            other = {k: v for k, v in other.items() if k in expected}

        if self.ignore:
            expected = self._filter_dict(self.expected_values)
            other = self._filter_dict(other)

        if other != expected:
            return False

        if self.strict and list(other.keys()) != list(expected.keys()):
            return False

        return True

    def _filter_dict(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        return {k: v for k, v in d.items() if not self._ignore_value(v)}

    def _ignore_value(self, v: Any) -> bool:
        if isinstance(v, (DirtyEquals, DirtyEqualsMeta)):
            return False
        elif callable(self.ignore):
            return self.ignore(v)
        else:
            try:
                return v in self.ignore  # type: ignore[operator]
            except TypeError:
                # happens for unhashable types
                return False

    def _repr_ne(self) -> str:
        name = self.__class__.__name__
        modifiers = []
        if self.partial != (name == 'IsPartialDict'):
            modifiers += [f'partial={self.partial}']
        if (self.ignore == {None}) != (name == 'IsIgnoreDict') or self.ignore not in (None, {None}):
            r = self.ignore.__name__ if callable(self.ignore) else repr(self.ignore)
            modifiers += [f'ignore={r}']
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

    ```py title="IsPartialDict"
    from dirty_equals import IsPartialDict

    assert {'a': 1, 'b': 2, 'c': 3} == IsPartialDict(a=1, b=2)

    assert {'a': 1, 'b': 2, 'c': 3} != IsPartialDict(a=1, b=3)
    assert {'a': 1, 'b': 2, 'd': 3} != IsPartialDict(a=1, b=2, c=3)

    # combining partial and strict
    assert {'a': 1, 'b': None, 'c': 3} == IsPartialDict(a=1, c=3).settings(strict=True)
    assert {'b': None, 'c': 3, 'a': 1} != IsPartialDict(a=1, c=3).settings(strict=True)
    ```
    """

    def _post_init(self) -> None:
        self.partial = True


class IsIgnoreDict(IsDict):
    """
    Dictionary comparison with `None` values ignored, this is the same as
    [`IsDict(...).settings(ignore={None})`][dirty_equals.IsDict.settings].

    `.settings(...)` can be used to customise the behaviour of `IsIgnoreDict`, in particular changing which
    values are ignored.

    ```py title="IsIgnoreDict"
    from dirty_equals import IsIgnoreDict

    assert {'a': 1, 'b': 2, 'c': None} == IsIgnoreDict(a=1, b=2)
    assert {'a': 1, 'b': 2, 'c': None, 'c': 'ignore'} == (
        IsIgnoreDict(a=1, b=2).settings(ignore={None, 'ignore'})
    )

    def is_even(v: int) -> bool:
        return v % 2 == 0

    assert {'a': 1, 'b': 2, 'c': 3, 'd': 4} == (
        IsIgnoreDict(a=1, c=3).settings(ignore=is_even)
    )

    # combining partial and strict
    assert {'a': 1, 'b': None, 'c': 3} == IsIgnoreDict(a=1, c=3).settings(strict=True)
    assert {'b': None, 'c': 3, 'a': 1} != IsIgnoreDict(a=1, c=3).settings(strict=True)
    ```
    """

    def _post_init(self) -> None:
        self.ignore = {None}


class IsStrictDict(IsDict):
    """
    Dictionary comparison with order enforced, this is the same as
    [`IsDict(...).settings(strict=True)`][dirty_equals.IsDict.settings].

    ```py title="IsDict.settings(...)"
    from dirty_equals import IsStrictDict

    assert {'a': 1, 'b': 2} == IsStrictDict(a=1, b=2)
    assert {'a': 1, 'b': 2, 'c': 3} != IsStrictDict(a=1, b=2)
    assert {'b': 2, 'a': 1} != IsStrictDict(a=1, b=2)

    # combining partial and strict
    assert {'a': 1, 'b': None, 'c': 3} == IsStrictDict(a=1, c=3).settings(partial=True)
    assert {'b': None, 'c': 3, 'a': 1} != IsStrictDict(a=1, c=3).settings(partial=True)
    ```
    """

    def _post_init(self) -> None:
        self.strict = True
