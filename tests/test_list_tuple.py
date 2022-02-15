import pytest

from dirty_equals import AnyThing, IsInt, IsList, IsListOrTuple, IsTuple


@pytest.mark.parametrize(
    'other,dirty',
    [
        ([], IsList),
        ((), IsTuple),
        ([], IsList()),
        ((), IsTuple()),
        ([1, 2, 3], IsList(1, 2, 3)),
        ((1, 2, 3), IsTuple(1, 2, 3)),
        ((1, 2, 3), IsListOrTuple(1, 2, 3)),
        ([1, 2, 3], IsListOrTuple(1, 2, 3)),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=5)),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=(4, 6))),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=(4, ...))),
        ([3, 2, 1], IsList(1, 2, 3, check_order=False)),
        ([{1: 2}, 7], IsList(7, {1: IsInt}, check_order=False)),
        ([1, 2, 3, 4], IsList(positions={0: 1, 2: 3, -1: 4})),
        ([1, 2, 3], IsList(AnyThing, 2, 3)),
    ],
)
def test_dirty_equals(other, dirty):
    assert other == dirty


@pytest.mark.parametrize(
    'other,dirty',
    [
        ([], IsTuple),
        ((), IsList),
        ([1, 2, 3], IsTuple(1, 2, 3)),
        ((1, 2, 3), IsList(1, 2, 3)),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=6)),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=(6, 8))),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=(0, 2))),
        ([1, 2, 3, 4, 5], IsList(1, 2, 3, length=(6, ...))),
        ([3, 2, 1, 4], IsList(1, 2, 3, check_order=False)),
        ([1, 2, 3, 4], IsList(positions={0: 1, 2: 3, -1: 5})),
    ],
)
def test_dirty_not_equals(other, dirty):
    assert other != dirty


def test_args_and_positions():
    with pytest.raises(TypeError, match='IsList requires either args or positions, not both'):
        IsList(1, 2, positions={0: 1})


def test_positions_with_check_order():
    with pytest.raises(TypeError, match='check_order=False is not compatible with positions'):
        IsList(check_order=False, positions={0: 1})
