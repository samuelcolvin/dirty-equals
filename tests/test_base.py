import pytest

from dirty_equals import IsApprox, IsInstanceOf, IsInt, IsNegative, IsPositive, IsStr


def test_or():
    assert 'foo' == IsStr | IsInt
    assert 1 == IsStr | IsInt
    assert -1 == IsStr | IsNegative | IsPositive

    v = IsStr | IsInt
    with pytest.raises(AssertionError):
        assert 1.5 == v
    assert str(v) == 'DirtyOr(IsStr | IsInt)'


def test_and():
    assert 4 == IsPositive & IsInt(lt=5)

    v = IsStr & IsInt
    with pytest.raises(AssertionError):
        assert 1 == v
    assert str(v) == 'DirtyAnd(IsStr & IsInt)'


def test_not():
    assert 'foo' != IsInt
    assert 'foo' == ~IsInt


def test_value_eq():
    v = IsStr()

    with pytest.raises(AttributeError, match='value is not available until __eq__ has been called'):
        v.value

    assert 'foo' == v
    assert str(v) == "'foo'"
    assert repr(v) == "'foo'"
    assert v.value == 'foo'


def test_value_ne():
    v = IsStr()

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == 'IsStr()'
    assert repr(v) == 'IsStr()'
    with pytest.raises(AttributeError, match='value is not available until __eq__ has been called'):
        v.value


class Foo:
    pass


def test_is_instance_of():
    assert Foo() == IsInstanceOf(Foo)
    assert Foo() == IsInstanceOf[Foo]
    assert 1 != IsInstanceOf[Foo]


class Bar(Foo):
    pass


def test_is_instance_of_inherit():
    assert Bar() == IsInstanceOf(Foo)
    assert Foo() == IsInstanceOf(Foo, only_direct_instance=True)
    assert Bar() != IsInstanceOf(Foo, only_direct_instance=True)

    assert Foo != IsInstanceOf(Foo)
    assert Bar != IsInstanceOf(Foo)
    assert type != IsInstanceOf(Foo)


def test_is_instance_of_repr():
    assert repr(IsInstanceOf) == 'IsInstanceOf'
    assert repr(IsInstanceOf(Foo)) == "IsInstanceOf(<class 'tests.test_base.Foo'>)"


def test_dict_compare():
    v = {'foo': 1, 'bar': 2, 'spam': 3}
    assert v == {'foo': IsInt, 'bar': IsPositive, 'spam': ~IsStr}
    assert v == {'foo': IsInt() & IsApprox(1), 'bar': IsPositive() | IsNegative(), 'spam': ~IsStr()}


def test_not_repr():
    v = ~IsInt

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == '~IsInt'


def test_is_approx_without_init():
    assert 1 != IsApprox
