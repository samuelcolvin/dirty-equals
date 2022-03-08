import pytest

from dirty_equals import IsFalseLike


@pytest.mark.parametrize(
    'other, expected',
    [
        (False, IsFalseLike),
        (True, ~IsFalseLike),
        ([], IsFalseLike),
        ([1], ~IsFalseLike),
        ((), IsFalseLike),
        ((1, 2), ~IsFalseLike),
        ({}, IsFalseLike),
        ({1: 'a'}, ~IsFalseLike),
        (set(), IsFalseLike),
        ({'a', 'b', 'c'}, ~IsFalseLike),
        (None, IsFalseLike),
        (object, ~IsFalseLike),
        (0, IsFalseLike(numeric=True)),
        (1, ~IsFalseLike(numeric=True)),
        (0.0, IsFalseLike(numeric=True)),
        (1.0, ~IsFalseLike(numeric=True)),
        ('0', IsFalseLike(string=True)),
        ('1', ~IsFalseLike(string=True)),
        ('0.0', IsFalseLike(string=True)),
        ('1.0', ~IsFalseLike(string=True)),
        ('False', IsFalseLike(string=True)),
        ('True', ~IsFalseLike(string=True)),
    ],
)
class TestIsFalseLike:
    def test_dirty_equals(self, other, expected):
        assert other == expected

    def test_dirty_not_equals(self, other, expected):
        with pytest.raises(AssertionError):
            assert other != expected


@pytest.mark.parametrize(
    'kwargs,error_message, error_type',
    [
        ({'numeric': True, 'string': True}, '"numeric" and "string" cannot be combined', TypeError),
        ({'numeric': 'I should be a boolean'}, '"numeric" requires a boolean argument', ValueError),
        ({'string': 'I should be a boolean'}, '"string" requires a boolean argument', ValueError),
    ],
)
def test_invalid_initialization(kwargs, error_message, error_type):
    with pytest.raises(error_type, match=error_message):
        IsFalseLike(**kwargs)
