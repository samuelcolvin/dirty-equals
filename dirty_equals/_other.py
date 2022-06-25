import json
import re
from typing import Any, Callable, TypeVar, overload
from uuid import UUID

from ._base import DirtyEquals
from ._utils import plain_repr

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore[misc]


class IsUUID(DirtyEquals[UUID]):
    """
    A class that checks if a value is a valid UUID, optionally checking UUID version.
    """

    def __init__(self, version: Literal[None, 1, 2, 3, 4, 5] = None):
        """
        Args:
            version: The version of the UUID to check, if omitted, all versions are accepted.

        ```py title="IsUUID"
        import uuid
        from dirty_equals import IsUUID

        assert 'edf9f29e-45c7-431c-99db-28ea44df9785' == IsUUID
        assert 'edf9f29e-45c7-431c-99db-28ea44df9785' == IsUUID(4)
        assert 'edf9f29e45c7431c99db28ea44df9785' == IsUUID(4)
        assert 'edf9f29e-45c7-431c-99db-28ea44df9785' != IsUUID(5)
        assert uuid.uuid4() == IsUUID(4)
        ```
        """
        self.version = version
        super().__init__(version or plain_repr('*'))

    def equals(self, other: Any) -> bool:
        if isinstance(other, UUID):
            uuid = other
        elif isinstance(other, str):
            uuid = UUID(other)
            if self.version is not None and uuid.version != self.version:
                return False
        else:
            return False

        if self.version:
            return uuid.version == self.version
        else:
            return True


AnyJson = object
JsonType = TypeVar('JsonType', AnyJson, Any)


class IsJson(DirtyEquals[JsonType]):
    """
    A class that checks if a value is a JSON object, and check the contents of the JSON.
    """

    @overload
    def __init__(self, expected_value: JsonType = AnyJson):
        ...

    @overload
    def __init__(self, **expected_kwargs: Any):
        ...

    def __init__(self, expected_value: JsonType = AnyJson, **expected_kwargs: Any):
        """
        Args:
            expected_value: Value to compare the JSON to, if omitted, any JSON is accepted.
            **expected_kwargs: Keyword arguments forming a dict to compare the JSON to,
                `expected_value` and `expected_kwargs` may not be combined.

        As with any `dirty_equals` type, types can be nested to provide more complex checks.

        !!! note
            Like [`IsInstance`][dirty_equals.IsInstance], `IsJson` can be parameterized or initialised with a value -
            `IsJson[xyz]` is exactly equivalent to `IsJson(xyz)`.

            This allows usage to be analogous to type hints.


        ```py title="IsJson"
        from dirty_equals import IsJson, IsStrictDict, IsPositiveInt

        assert '{"a": 1, "b": 2}' == IsJson
        assert '{"a": 1, "b": 2}' == IsJson(a=1, b=2)
        assert '{"a": 1}' != IsJson(a=2)
        assert 'invalid json' != IsJson
        assert '{"a": 1}' == IsJson(a=IsPositiveInt)
        assert '"just a quoted string"' == IsJson('just a quoted string')

        assert '{"a": 1, "b": 2}' == IsJson[IsStrictDict(a=1, b=2)]
        assert '{"b": 2, "a": 1}' != IsJson[IsStrictDict(a=1, b=2)]
        ```
        """
        if expected_kwargs:
            if expected_value is not AnyJson:
                raise TypeError('IsJson requires either an argument or kwargs, not both')
            self.expected_value: Any = expected_kwargs
        else:
            self.expected_value = expected_value
        super().__init__(plain_repr('*') if expected_value is AnyJson else expected_value)

    def __class_getitem__(cls, expected_type: JsonType) -> 'IsJson[JsonType]':
        return cls(expected_type)

    def equals(self, other: Any) -> bool:
        if isinstance(other, (str, bytes)):
            v = json.loads(other)
            if self.expected_value is AnyJson:
                return True
            else:
                return v == self.expected_value
        else:
            return False


class FunctionCheck(DirtyEquals[Any]):
    """
    Use a function to check if a value "equals" whatever you want to check
    """

    def __init__(self, func: Callable[[Any], bool]):
        """
        Args:
            func: callable that takes a value and returns a bool.

        ```py title="FunctionCheck"
        from dirty_equals import FunctionCheck

        def is_even(x):
            return x % 2 == 0

        assert 2 == FunctionCheck(is_even)
        assert 3 != FunctionCheck(is_even)
        ```
        """
        self.func = func
        super().__init__(plain_repr(func.__name__))

    def equals(self, other: Any) -> bool:
        return self.func(other)


class IsHash(DirtyEquals[str]):
    """
    A class that checks if a value is a valid common hash type, using a simple length and allowed characters regex.
    """

    def __init__(self, hash_type: Literal['md5', 'sha-1', 'sha-256']):
        """
        Args:
            hash_type: The hash type to check. Must be specified.

        ```py title="IsUUID"
        from dirty_equals import IsHash

        assert 'f1e069787ece74531d112559945c6871' == IsHash('md5')
        assert 'f1e069787ece74531d112559945c6871' != IsHash('sha-256')
        assert 'F1E069787ECE74531D112559945C6871' == IsHash('md5')
        assert '40bd001563085fc35165329ea1ff5c5ecbdbbeef' == IsHash('sha-1')
        assert 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3' == IsHash('sha-256')
        ```
        """

        allowed_hashes = 'md5', 'sha-1', 'sha-256'
        if hash_type not in allowed_hashes:
            raise ValueError(f"Hash type must be one of the following values: {', '.join(allowed_hashes)}")

        self.hash_type = hash_type
        super().__init__(hash_type)

    def equals(self, other: Any) -> bool:
        hash_type_regex_patterns = {
            'md5': r'^[a-fA-F\d]{32}$',
            'sha-1': r'^[a-fA-F\d]{40}$',
            'sha-256': r'^[a-fA-F\d]{64}$',
        }
        return bool(re.fullmatch(hash_type_regex_patterns[self.hash_type], other))
