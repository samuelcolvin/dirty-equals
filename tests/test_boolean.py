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
        (0, IsFalseLike),
        (1, ~IsFalseLike),
        (0.0, IsFalseLike),
        (1.0, ~IsFalseLike),
        ('0', IsFalseLike(allow_strings=True)),
        ('1', ~IsFalseLike(allow_strings=True)),
        ('0.0', IsFalseLike(allow_strings=True)),
        ('1.0', ~IsFalseLike(allow_strings=True)),
        ('False', IsFalseLike(allow_strings=True)),
        ('True', ~IsFalseLike(allow_strings=True)),
    ],
)
class TestIsFalseLike:
    def test_dirty_equals(self, other, expected):
        assert other == expected

    def test_dirty_not_equals(self, other, expected):
        with pytest.raises(AssertionError):
            assert other != expected


def test_invalid_initialization():
    with pytest.raises(TypeError, match='takes 1 positional argument but 2 were given'):
        IsFalseLike(True)
