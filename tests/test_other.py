import uuid

import pytest

from dirty_equals import FunctionCheck, IsJson, IsUUID


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
