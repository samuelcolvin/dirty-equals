from typing import Any, Callable, Container, Dict, Optional, Union

from dirty_equals._base import DirtyEquals


class IsDict(DirtyEquals[Dict[Any, Any]]):
    def __init__(self, __expected_values: Optional[Dict[Any, Any]] = None, **expected_kwargs: Any) -> None:
        if expected_kwargs:
            self.expected_values = expected_kwargs
            if __expected_values is not None:
                raise TypeError('IsDict requires either a single argument or kwargs, not both')
        else:
            self.expected_values = __expected_values or {}

        if not isinstance(self.expected_values, dict):
            raise TypeError(f'expected_values must be a dict, got {type(self.expected_values)}')

        self.strict_order = False
        self.partial = False
        self.ignore_values: Union[Container[Any], Callable[[Any], bool]] = {None}
        self._post_init()
        super().__init__()

    def _post_init(self) -> None:
        pass

    def settings(
        self,
        *,
        strict_order: Optional[bool] = None,
        partial: Optional[bool] = None,
        ignore_values: Union[None, Container[Any], Callable[[Any], bool]] = None,
    ) -> 'IsDict':
        new_dict = IsDict(**self.expected_values)
        if strict_order is not None:
            new_dict.strict_order = strict_order
        if partial is not None:
            new_dict.partial = partial
        if ignore_values is not None:
            new_dict.ignore_values = ignore_values
        return new_dict

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

        if self.strict_order and list(other.keys()) != list(expected.keys()):
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
        if self.ignore_values != {None} or name != 'IsPartialDict':
            modifiers += [f'ignore_values={self.ignore_values!r}']
        if self.strict_order != (name == 'IsStrictDict'):
            modifiers += [f'strict_order={self.strict_order}']

        if modifiers:
            mod = f'[{", ".join(modifiers)}]'
        else:
            mod = ''

        args = [f'{k}={v!r}' for k, v in self.expected_values.items()]
        return f'{name}{mod}({", ".join(args)})'


class IsPartialDict(IsDict):
    def _post_init(self) -> None:
        self.partial = True


class IsStrictDict(IsDict):
    def _post_init(self) -> None:
        self.strict_order = True
