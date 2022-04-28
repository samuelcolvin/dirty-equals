import platform

import pytest

from dirty_equals import Contains, IsApprox, IsInt, IsNegative, IsOneOf, IsPositive, IsStr


def test_or():
    assert 'foo' == IsStr | IsInt
    assert 1 == IsStr | IsInt
    assert -1 == IsStr | IsNegative | IsPositive

    v = IsStr | IsInt
    with pytest.raises(AssertionError):
        assert 1.5 == v
    assert str(v) == 'IsStr | IsInt'


def test_and():
    assert 4 == IsPositive & IsInt(lt=5)

    v = IsStr & IsInt
    with pytest.raises(AssertionError):
        assert 1 == v
    assert str(v) == 'IsStr & IsInt'


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


def test_dict_compare():
    v = {'foo': 1, 'bar': 2, 'spam': 3}
    assert v == {'foo': IsInt, 'bar': IsPositive, 'spam': ~IsStr}
    assert v == {'foo': IsInt() & IsApprox(1), 'bar': IsPositive() | IsNegative(), 'spam': ~IsStr()}


@pytest.mark.skipif(platform.python_implementation() == 'PyPy', reason='PyPy does not metaclass dunder methods')
def test_not_repr():
    v = ~IsInt
    assert str(v) == '~IsInt'

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == '~IsInt'


def test_not_repr_instance():
    v = ~IsInt()
    assert str(v) == '~IsInt()'

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == '~IsInt()'


def test_repr():
    v = ~IsInt
    assert str(v) == '~IsInt'

    assert '1' == v

    assert str(v) == "'1'"


@pytest.mark.parametrize(
    'v,v_repr',
    [
        (IsInt, 'IsInt'),
        (~IsInt, '~IsInt'),
        (IsInt & IsPositive, 'IsInt & IsPositive'),
        (IsInt | IsPositive, 'IsInt | IsPositive'),
        (IsInt(), 'IsInt()'),
        (~IsInt(), '~IsInt()'),
        (IsInt() & IsPositive(), 'IsInt() & IsPositive()'),
        (IsInt() | IsPositive(), 'IsInt() | IsPositive()'),
        (IsInt() & IsPositive, 'IsInt() & IsPositive'),
        (IsInt() | IsPositive, 'IsInt() | IsPositive'),
        (IsPositive & IsInt(lt=5), 'IsPositive & IsInt(lt=5)'),
        (IsOneOf(1, 2, 3), 'IsOneOf(1, 2, 3)'),
    ],
)
def test_repr_class(v, v_repr):
    assert repr(v) == v_repr


def test_is_approx_without_init():
    assert 1 != IsApprox


def test_ne_repr():
    v = IsInt
    assert repr(v) == 'IsInt'

    assert 'x' != v

    assert repr(v) == 'IsInt'


@pytest.mark.parametrize(
    'value,dirty',
    [
        (1, IsOneOf(1, 2, 3)),
        (4, ~IsOneOf(1, 2, 3)),
        ([1, 2, 3], Contains(1) | IsOneOf([])),
        ([], Contains(1) | IsOneOf([])),
        ([2], ~(Contains(1) | IsOneOf([]))),
    ],
)
def test_is_one_of(value, dirty):
    assert value == dirty
