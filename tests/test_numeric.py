import pytest

from dirty_equals import IsFloat, IsInt, IsNegativeFloat, IsNegativeInt, IsPositiveFloat, IsPositiveInt


@pytest.mark.parametrize('other,dirty', [(1, IsInt), (1, IsInt()), (1, IsPositiveInt), (-1, IsNegativeInt)])
def test_dirty_equals_int(other, dirty):
    assert dirty == other


@pytest.mark.parametrize('other,dirty', [(-1.0, IsFloat), (1.0, IsPositiveFloat), (-1.0, IsNegativeFloat)])
def test_dirty_equals_float(other, dirty):
    assert dirty == other


def test_not_int():
    d = IsInt
    with pytest.raises(AssertionError):
        assert '1' == d
    assert repr(d) == 'IsInt()'


def test_not_negative():
    d = IsNegativeInt
    with pytest.raises(AssertionError):
        assert 1 == d
    assert repr(d) == 'IsNegativeInt()'
