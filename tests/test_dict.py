import pytest

from dirty_equals import IsDict, IsPartialDict, IsStrictDict


@pytest.mark.parametrize(
    'input_value,expected',
    [
        ({}, IsDict),
        ({}, IsDict()),
        ({'a': 1}, IsDict(a=1)),
        ({1: 2}, IsDict({1: 2})),
        ({'a': 1, 'b': 2}, IsDict(a=1, b=2)),
        ({'b': 2, 'a': 1}, IsDict(a=1, b=2)),
        ({'a': 1, 'b': None}, IsDict(a=1, b=None)),
        ({'a': 1, 'b': 3}, ~IsDict(a=1, b=2)),
        # partial dict
        ({}, IsPartialDict()),
        ({'a': 1, 'b': 2}, IsPartialDict(a=1, b=2)),
        ({'a': 1, 'b': None}, IsPartialDict(a=1)),
        ({1: 10, 2: None}, IsPartialDict({1: 10})),
        ({'a': 1, 'b': 2}, ~IsPartialDict(a=1)),
        ({1: 10, 2: None}, IsDict({1: 10}).settings(partial=True)),
        ({1: 10, 2: False}, ~IsPartialDict({1: 10})),
        ({1: 10, 2: False}, IsPartialDict({1: 10}).settings(ignore_values={False})),
        # strict dict
        ({}, IsStrictDict()),
        ({'a': 1, 'b': 2}, IsStrictDict(a=1, b=2)),
        ({'a': 1, 'b': 2}, ~IsStrictDict(b=2, a=1)),
        ({1: 10, 2: 20}, IsStrictDict({1: 10, 2: 20})),
        ({1: 10, 2: 20}, ~IsStrictDict({2: 20, 1: 10})),
        ({1: 10, 2: 20}, ~IsDict({2: 20, 1: 10}).settings(strict=True)),
    ],
)
def test_is_dict(input_value, expected):
    assert input_value == expected


def test_ne_repr_partial_dict():
    v = IsPartialDict({1: 10, 2: 20})

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == 'IsPartialDict(1=10, 2=20)'


def test_ne_repr_strict_dict():
    v = IsStrictDict({1: 10, 2: 20})

    with pytest.raises(AssertionError):
        assert 1 == v

    assert str(v) == 'IsStrictDict(1=10, 2=20)'
