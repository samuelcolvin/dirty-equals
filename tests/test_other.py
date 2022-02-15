import uuid

import pytest

from dirty_equals import FunctionCheck, IsJson, IsUUID


def test_is_uuid_true():
    is_uuid = IsUUID()
    uuid_ = uuid.uuid4()
    assert uuid_ == is_uuid
    assert str(is_uuid) == repr(uuid_)


def test_is_uuid_false():
    is_uuid = IsUUID()
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(*)'


def test_is_uuid4_false():
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
