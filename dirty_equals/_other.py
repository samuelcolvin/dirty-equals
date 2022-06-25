import json
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, ip_network
from typing import Any, Callable, Optional, TypeVar, Union, overload
from uuid import UUID

from ._base import DirtyEquals
from ._utils import Omit, plain_repr

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


IP = TypeVar('IP', IPv4Address, IPv4Network, IPv6Address, IPv6Network, Union[str, int, bytes])


class IsIP(DirtyEquals[IP]):
    """
    A class that checks if a value is a valid IP address, optionally checking IP version, netmask.
    """

    def __init__(self, *, version: Literal[None, 4, 6] = None, netmask: Optional[str] = None):
        """
        Args:
            version: The version of the IP to check, if omitted, versions 4 and 6 are both accepted.
            netmask: The netmask of the IP to check, if omitted, any netmask is accepted. Requires version.

        ```py title="IsIP"
        from ipaddress import IPv4Address, IPv6Address, IPv4Network
        from dirty_equals import IsIP

        assert '179.27.154.96' == IsIP
        assert '179.27.154.96' == IsIP(version=4)
        assert '2001:0db8:0a0b:12f0:0000:0000:0000:0001' == IsIP(version=6)
        assert IPv4Address('127.0.0.1') == IsIP
        assert IPv4Network('43.48.0.0/12') == IsIP
        assert IPv6Address('::eeff:ae3f:d473') == IsIP
        assert '54.43.53.219/10' == IsIP(version=4, netmask='255.192.0.0')
        assert '54.43.53.219/10' == IsIP(version=4, netmask=4290772992)
        assert '::ffff:aebf:d473/12' == IsIP(version=6, netmask='fff0::')
        assert 3232235521 == IsIP
        ```
        """
        self.version = version
        if netmask and not self.version:
            raise TypeError('To check the netmask you must specify the IP version')
        self.netmask = netmask
        super().__init__(version=version or Omit, netmask=netmask or Omit)

    def equals(self, other: Any) -> bool:

        if isinstance(other, (IPv4Network, IPv6Network)):
            ip = other
        elif isinstance(other, (str, bytes, int, IPv4Address, IPv6Address)):
            ip = ip_network(other, strict=False)
        else:
            return False

        if self.version:
            if self.netmask:
                version_check = self.version == ip.version
                address_format = {4: IPv4Address, 6: IPv6Address}[self.version]
                netmask_check = int(address_format(self.netmask)) == int(ip.netmask)
                return version_check and netmask_check
            elif self.version != ip.version:
                return False

        return True
