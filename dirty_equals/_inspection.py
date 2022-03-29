from typing import Any, Tuple, TypeVar, Union

from ._base import DirtyEquals

ExpectedType = TypeVar('ExpectedType', bound=Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]])


class IsInstance(DirtyEquals[ExpectedType]):
    """
    A type which checks that the value is an instance of the expected type.
    """

    def __init__(self, expected_type: ExpectedType, *, only_direct_instance: bool = False):
        """
        Args:
            expected_type: The type to check against.
            only_direct_instance: whether instances of subclasses of `expected_type` should be considered equal.

        !!! note
            `IsInstance` can be parameterized or initialised with a type -
            `IsInstance[Foo]` is exactly equivalent to `IsInstance(Foo)`.

            This allows usage to be analogous to type hints.

        Example:
        ```py title="IsInstance"
        from dirty_equals import IsInstance

        class Foo:
            pass

        class Bar(Foo):
            pass

        assert Foo() == IsInstance[Foo]
        assert Foo() == IsInstance(Foo)
        assert Foo != IsInstance[Bar]

        assert Bar() == IsInstance[Foo]
        assert Foo() == IsInstance(Foo, only_direct_instance=True)
        assert Bar() != IsInstance(Foo, only_direct_instance=True)
        ```
        """
        self.expected_type = expected_type
        self.only_direct_instance = only_direct_instance
        super().__init__(expected_type)

    def __class_getitem__(cls, expected_type: ExpectedType) -> 'IsInstance[ExpectedType]':
        return cls(expected_type)

    def equals(self, other: Any) -> bool:
        if self.only_direct_instance:
            return type(other) == self.expected_type
        else:
            return isinstance(other, self.expected_type)


HasNameType = TypeVar('HasNameType')


class HasName(DirtyEquals[HasNameType]):
    """
    A type which checks that the value has the given `__name__` attribute.
    """

    def __init__(self, expected_name: str, *, allow_instances: bool = True):
        """
        Args:
            expected_name: The name to check against.
            allow_instances: whether instances of classes with the given name should be considered equal,
                (e.g. whether `other.__class__.__name__ == expected_name` should be checked).

        Example:
        ```py title="HasName"
        from dirty_equals import HasName, IsStr

        class Foo:
            pass

        assert Foo == HasName('Foo')
        assert Foo == HasName['Foo']
        assert Foo() == HasName('Foo')
        assert Foo() != HasName('Foo', allow_instances=False)
        assert Foo == HasName(IsStr(regex='F..'))
        assert Foo != HasName('Bar')
        assert int == HasName('int')
        assert int == HasName('int')
        ```
        """
        self.expected_name = expected_name
        self.allow_instances = allow_instances
        kwargs = {}
        if allow_instances:
            kwargs['allow_instances'] = allow_instances
        super().__init__(expected_name, allow_instances=allow_instances)

    def __class_getitem__(cls, expected_name: str) -> 'HasName[HasNameType]':
        return cls(expected_name)

    def equals(self, other: Any) -> bool:
        direct_name = getattr(other, '__name__', None) == self.expected_name
        if direct_name:
            return True

        if self.allow_instances:
            cls = getattr(other, '__class__', None)
            if cls is not None and getattr(cls, '__name__', None) == self.expected_name:
                return True

        return False
