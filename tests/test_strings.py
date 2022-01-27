import pytest

from dirty_equals import IsAnyStr, IsBytes, IsStr


def test_simple():
    assert 'foo' == IsStr


def test_regex_true():
    assert 'whatever' == IsStr(regex='whatever')
    reg = IsStr(regex='wh.*er')
    assert 'whatever' == reg
    assert str(reg) == "'whatever'"


def test_regex_bytes_true():
    assert b'whatever' == IsBytes(regex=b'whatever')
    assert b'whatever' == IsBytes(regex=b'wh.*er')


def test_regex_false():
    reg = IsStr(regex='wh.*er')
    with pytest.raises(AssertionError):
        assert 'WHATEVER' == reg
    assert str(reg) == "IsStr(regex='wh.*er')"


def test_regex_false_type_error():
    assert 123 != IsStr(regex='wh.*er')

    reg = IsBytes(regex=b'wh.*er')
    with pytest.raises(AssertionError):
        assert 'whatever' == reg
    assert str(reg) == "IsBytes(regex=b'wh.*er')"


def test_is_any_str():
    assert 'foobar' == IsAnyStr
    assert b'foobar' == IsAnyStr
    assert 123 != IsAnyStr
    assert 'foo' == IsAnyStr(regex='foo')
    assert 'foo' == IsAnyStr(regex=b'foo')
    assert b'foo' == IsAnyStr(regex='foo')
    assert b'foo' == IsAnyStr(regex=b'foo')
