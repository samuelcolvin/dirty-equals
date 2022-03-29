import pytest

from dirty_equals import AnyThing, HasAttributes, HasName, IsInstance, IsInt, IsStr


class Foo:
    def __init__(self, a=1, b=2):
        self.a = a
        self.b = b

    def spam(self):
        pass


def test_is_instance_of():
    assert Foo() == IsInstance(Foo)
    assert Foo() == IsInstance[Foo]
    assert 1 != IsInstance[Foo]


class Bar(Foo):
    pass


def test_is_instance_of_inherit():
    assert Bar() == IsInstance(Foo)
    assert Foo() == IsInstance(Foo, only_direct_instance=True)
    assert Bar() != IsInstance(Foo, only_direct_instance=True)

    assert Foo != IsInstance(Foo)
    assert Bar != IsInstance(Foo)
    assert type != IsInstance(Foo)


def test_is_instance_of_repr():
    assert repr(IsInstance) == 'IsInstance'
    assert repr(IsInstance(Foo)) == "IsInstance(<class 'tests.test_inspection.Foo'>)"


def even(x):
    return x % 2 == 0


@pytest.mark.parametrize(
    'value,dirty',
    [
        (Foo, HasName('Foo')),
        (Foo, HasName['Foo']),
        (Foo(), HasName('Foo')),
        (Foo(), ~HasName('Foo', allow_instances=False)),
        (Bar, ~HasName('Foo')),
        (int, HasName('int')),
        (42, HasName('int')),
        (even, HasName('even')),
        (Foo().spam, HasName('spam')),
        (Foo.spam, HasName('spam')),
        (Foo, HasName(IsStr(regex='F..'))),
        (Bar, ~HasName(IsStr(regex='F..'))),
    ],
)
def test_has_name(value, dirty):
    assert value == dirty


@pytest.mark.parametrize(
    'value,dirty',
    [
        (Foo(1, 2), HasAttributes(a=1, b=2)),
        (Foo(1, 's'), HasAttributes(a=IsInt, b=IsStr)),
        (Foo(1, 2), ~HasAttributes(a=IsInt, b=IsStr)),
        (Foo(1, 2), ~HasAttributes(a=1, b=2, c=3)),
        (Foo(1, 2), HasAttributes(a=1, b=2, spam=AnyThing)),
        (Foo(1, 2), ~HasAttributes(a=1, b=2, missing=AnyThing)),
    ],
)
def test_has_attributes(value, dirty):
    assert value == dirty
