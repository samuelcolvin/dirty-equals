import pytest

from dirty_equals import IsFalseLike, IsTrueLike


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
        ('0.000', IsFalseLike(allow_strings=True)),
        ('1.0', ~IsFalseLike(allow_strings=True)),
        ('False', IsFalseLike(allow_strings=True)),
        ('True', ~IsFalseLike(allow_strings=True)),
        (0, IsFalseLike(allow_strings=True)),
    ],
)
def test_is_false_like(other, expected):
    assert other == expected


def test_dirty_not_equals():
    with pytest.raises(AssertionError):
        assert 0 != IsFalseLike


def test_invalid_initialization():
    with pytest.raises(TypeError, match='takes 1 positional argument but 2 were given'):
        IsFalseLike(True)


@pytest.mark.parametrize(
    'other, expected',
    [
        (False, ~IsTrueLike),
        (True, IsTrueLike),
        ([], ~IsTrueLike),
        ([1], IsTrueLike),
        ((), ~IsTrueLike),
        ((1, 2), IsTrueLike),
        ({}, ~IsTrueLike),
        ({1: 'a'}, IsTrueLike),
        (set(), ~IsTrueLike),
        ({'a', 'b', 'c'}, IsTrueLike),
        (None, ~IsTrueLike),
        (object, IsTrueLike),
        (0, ~IsTrueLike),
        (1, IsTrueLike),
        (0.0, ~IsTrueLike),
        (1.0, IsTrueLike),
    ],
)
def test_is_true_like(other, expected):
    assert other == expected
