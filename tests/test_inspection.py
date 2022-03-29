import pytest

from dirty_equals import HasName, IsInstance, IsStr


class Foo:
    def snap(self):
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
    'type,dirty',
    [
        (Foo, HasName('Foo')),
        (Foo, HasName['Foo']),
        (Foo(), HasName('Foo')),
        (Foo(), ~HasName('Foo', allow_instances=False)),
        (Bar, ~HasName('Foo')),
        (int, HasName('int')),
        (42, HasName('int')),
        (even, HasName('even')),
        (Foo, HasName(IsStr(regex='F..'))),
        (Bar, ~HasName(IsStr(regex='F..'))),
    ],
)
def test_has_name(type, dirty):
    assert type == dirty
