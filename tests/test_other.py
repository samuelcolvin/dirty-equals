import uuid
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

import pytest

from dirty_equals import FunctionCheck, IsIP, IsJson, IsUUID


@pytest.mark.parametrize(
    'other,dirty',
    [
        (uuid.uuid4(), IsUUID()),
        (uuid.uuid4(), IsUUID),
        (uuid.uuid4(), IsUUID(4)),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(4)),
        ('edf9f29e45c7431c99db28ea44df9785', IsUUID(4)),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID(3)),
        (uuid.uuid1(), IsUUID(1)),
        (str(uuid.uuid1()), IsUUID(1)),
        ('ea9e828d-fd18-3898-99f3-5a46dbcee036', IsUUID(3)),
    ],
)
def test_is_uuid_true(other, dirty):
    assert other == dirty


@pytest.mark.parametrize(
    'other,dirty',
    [
        ('foobar', IsUUID()),
        ([1, 2, 3], IsUUID()),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(5)),
        (uuid.uuid3(uuid.UUID('edf9f29e-45c7-431c-99db-28ea44df9785'), 'abc'), IsUUID(4)),
        (uuid.uuid1(), IsUUID(4)),
        ('edf9f29e-45c7-431c-99db-28ea44df9785', IsUUID(1)),
        ('ea9e828d-fd18-3898-99f3-5a46dbcee036', IsUUID(4)),
    ],
)
def test_is_uuid_false(other, dirty):
    assert other != dirty


def test_is_uuid_false_repr():
    is_uuid = IsUUID()
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(*)'


def test_is_uuid4_false_repr():
    is_uuid = IsUUID(4)
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(4)'


@pytest.mark.parametrize('json_value', ['null', '"xyz"', '[1, 2, 3]', '{"a": 1}'])
def test_is_json_any_true(json_value):
    assert json_value == IsJson()
    assert json_value == IsJson


def test_is_json_any_false():
    is_json = IsJson()
    with pytest.raises(AssertionError):
        assert 'foobar' == is_json
    assert str(is_json) == 'IsJson(*)'


@pytest.mark.parametrize(
    'json_value,expected_value',
    [
        ('null', None),
        ('"xyz"', 'xyz'),
        ('[1, 2, 3]', [1, 2, 3]),
        ('{"a": 1}', {'a': 1}),
    ],
)
def test_is_json_specific_true(json_value, expected_value):
    assert json_value == IsJson(expected_value)
    assert json_value == IsJson[expected_value]


def test_is_json_invalid():
    assert 'invalid json' != IsJson
    assert 123 != IsJson
    assert [1, 2] != IsJson


def test_is_json_kwargs():
    assert '{"a": 1, "b": 2}' == IsJson(a=1, b=2)
    assert '{"a": 1, "b": 3}' != IsJson(a=1, b=2)


def test_is_json_specific_false():
    is_json = IsJson([1, 2, 3])
    with pytest.raises(AssertionError):
        assert '{"a": 1}' == is_json
    assert str(is_json) == 'IsJson([1, 2, 3])'


def test_equals_function():
    func_argument = None

    def foo(v):
        nonlocal func_argument
        func_argument = v
        return v % 2 == 0

    assert 4 == FunctionCheck(foo)
    assert func_argument == 4
    assert 5 != FunctionCheck(foo)


def test_equals_function_fail():
    def foobar(v):
        return False

    c = FunctionCheck(foobar)

    with pytest.raises(AssertionError):
        assert 4 == c

    assert str(c) == 'FunctionCheck(foobar)'


def test_json_both():
    with pytest.raises(TypeError, match='IsJson requires either an argument or kwargs, not both'):
        IsJson(1, a=2)


@pytest.mark.parametrize(
    'other,dirty',
    [
        (IPv4Address('127.0.0.1'), IsIP()),
        (IPv4Network('43.48.0.0/12'), IsIP()),
        (IPv6Address('::eeff:ae3f:d473'), IsIP()),
        (IPv6Network('::eeff:ae3f:d473/128'), IsIP()),
        ('2001:0db8:0a0b:12f0:0000:0000:0000:0001', IsIP()),
        ('179.27.154.96', IsIP),
        ('43.62.123.119', IsIP(version=4)),
        ('::ffff:2b3e:7b77', IsIP(version=6)),
        ('0:0:0:0:0:ffff:2b3e:7b77', IsIP(version=6)),
        ('54.43.53.219/10', IsIP(version=4, netmask='255.192.0.0')),
        ('::ffff:aebf:d473/12', IsIP(version=6, netmask='fff0::')),
        ('2001:0db8:0a0b:12f0:0000:0000:0000:0001', IsIP(version=6)),
        (3232235521, IsIP()),
        (b'\xC0\xA8\x00\x01', IsIP()),
        (338288524927261089654018896845572831328, IsIP(version=6)),
        (b'\x20\x01\x06\x58\x02\x2a\xca\xfe\x02\x00\x00\x00\x00\x00\x00\x01', IsIP(version=6)),
    ],
)
def test_is_ip_true(other, dirty):
    assert other == dirty


@pytest.mark.parametrize(
    'other,dirty',
    [
        ('foobar', IsIP()),
        ([1, 2, 3], IsIP()),
        ('210.115.28.193', IsIP(version=6)),
        ('::ffff:d273:1cc1', IsIP(version=4)),
        ('210.115.28.193/12', IsIP(version=6, netmask='255.255.255.0')),
        ('::ffff:d273:1cc1', IsIP(version=6, netmask='fff0::')),
        (3232235521, IsIP(version=6)),
        (338288524927261089654018896845572831328, IsIP(version=4)),
    ],
)
def test_is_ip_false(other, dirty):
    assert other != dirty


def test_not_ip_repr():
    is_ip = IsIP()
    with pytest.raises(AssertionError):
        assert '123' == is_ip
    assert str(is_ip) == 'IsIP()'


def test_ip_bad_netmask():
    with pytest.raises(TypeError, match='To check the netmask you must specify the IP version'):
        IsIP(netmask='255.255.255.0')
