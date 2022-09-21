import json
from typing import Any, Callable, Set, TypeVar, overload
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


class IsUrl(DirtyEquals):
    """
    A class that checks if a value is a valid URL, optionally checking different URL types and attributes with
    [Pydantic](https://pydantic-docs.helpmanual.io/usage/types/#urls).
    """

    allowed_attribute_checks: Set[str] = {
        'scheme',
        'host',
        'host_type',
        'user',
        'password',
        'tld',
        'port',
        'path',
        'query',
        'fragment',
    }

    def __init__(
            self,
            any_url: bool = False,
            any_http_url: bool = False,
            http_url: bool = False,
            file_url: bool = False,
            postgres_dsn: bool = False,
            ampqp_dsn: bool = False,
            redis_dsn: bool = False,
            **expected_attributes: Any,
    ):
        """
        Args:
            any_url: any scheme allowed, TLD not required, host required
            any_http_url: scheme http or https, TLD not required, host required
            http_url: scheme http or https, TLD required, host required, max length 2083
            file_url: scheme file, host not required
            postgres_dsn: user info required, TLD not required
            ampqp_dsn: schema amqp or amqps, user info not required, TLD not required, host not required
            redis_dsn: scheme redis or rediss, user info not required, tld not required, host not required
            **expected_attributes: Expected values for url attributes
        ```py title="IsUrl"
        from dirty_equals import IsUrl

        assert 'https://example.com' == IsUrl
        assert 'https://example.com' == IsUrl(tld='com')
        assert 'https://example.com' == IsUrl(scheme='https')
        assert 'https://example.com' != IsUrl(scheme='http')
        assert 'postgres://user:pass@localhost:5432/app' == IsUrl(postgres_dsn=True)
        assert 'postgres://user:pass@localhost:5432/app' != IsUrl(http_url=True)
        ```
        """
        try:
            from pydantic import AmqpDsn, AnyHttpUrl, AnyUrl, FileUrl, HttpUrl, PostgresDsn, RedisDsn, parse_obj_as, \
                ValidationError
            self.AmqpDsn = AmqpDsn
            self.AnyHttpUrl = AnyHttpUrl
            self.AnyUrl = AnyUrl
            self.FileUrl = FileUrl
            self.HttpUrl = HttpUrl
            self.PostgresDsn = PostgresDsn
            self.RedisDsn = RedisDsn
            self.parse_obj_as = parse_obj_as
            self.ValidationError = ValidationError
        except ImportError as e:
            raise ImportError('pydantic is not installed, run `pip install dirty-equals[pydantic]`') from e
        url_type_mappings = {any_url: self.AnyUrl,
                             any_http_url: self.AnyHttpUrl,
                             http_url: self.HttpUrl,
                             file_url: self.FileUrl,
                             postgres_dsn: self.PostgresDsn,
                             ampqp_dsn: self.AmqpDsn,
                             redis_dsn: self.RedisDsn}
        url_types_sum = sum(url_type_mappings.keys())
        if url_types_sum > 1:
            raise ValueError('You can only check against one Pydantic url type at a time')
        for item in expected_attributes:
            if item not in self.allowed_attribute_checks:
                raise TypeError(
                    'IsURL only checks these attributes: scheme, host, host_type, user, password, tld, '
                    'port, path, query, fragment'
                )
        self.attribute_checks = expected_attributes
        url_type = AnyUrl if url_types_sum == 0 else url_type_mappings[True]
        self.url_type = url_type
        super().__init__(url_type)

    def equals(self, other: Any) -> bool:

        try:
            parsed = self.parse_obj_as(self.url_type, other)
        except self.ValidationError:
            raise ValueError("Invalid URL")
        if not self.attribute_checks:
            return parsed == other

        for attribute, expected in self.attribute_checks.items():
            if getattr(parsed, attribute) != expected:
                return False
        return parsed == other
