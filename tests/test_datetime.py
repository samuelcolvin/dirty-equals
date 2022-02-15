from datetime import datetime, timedelta, timezone

import pytest
import pytz

from dirty_equals import IsDatetime, IsNow


@pytest.mark.parametrize(
    'value,is_dt,expect_match',
    [
        pytest.param(datetime(2000, 1, 1), IsDatetime(approx=datetime(2000, 1, 1)), True, id='same'),
        pytest.param(946684800, IsDatetime(approx=datetime(2000, 1, 1), unix_number=True), True, id='unix-int'),
        pytest.param(946684800.123, IsDatetime(approx=datetime(2000, 1, 1), unix_number=True), True, id='unix-float'),
        pytest.param(946684800, IsDatetime(approx=datetime(2000, 1, 1)), False, id='unix-different'),
        pytest.param(
            '2000-01-01T00:00', IsDatetime(approx=datetime(2000, 1, 1), iso_string=True), True, id='iso-string-true'
        ),
        pytest.param('2000-01-01T00:00', IsDatetime(approx=datetime(2000, 1, 1)), False, id='iso-string-different'),
        pytest.param('broken', IsDatetime(approx=datetime(2000, 1, 1)), False, id='iso-string-wrong'),
        pytest.param(
            '28/01/87', IsDatetime(approx=datetime(1987, 1, 28), format_string='%d/%m/%y'), True, id='string-format'
        ),
        pytest.param('28/01/87', IsDatetime(approx=datetime(2000, 1, 1)), False, id='string-format-different'),
        pytest.param('foobar', IsDatetime(approx=datetime(2000, 1, 1)), False, id='string-format-wrong'),
        pytest.param(datetime.now().isoformat(), IsNow(iso_string=True), True, id='isnow-str-true'),
        pytest.param(datetime(2000, 1, 1).isoformat(), IsNow(iso_string=True), False, id='isnow-str-different'),
        pytest.param([1, 2, 3], IsDatetime(approx=datetime(2000, 1, 1)), False, id='wrong-type'),
        pytest.param(
            datetime(2020, 1, 1, 12, 13, 14), IsDatetime(approx=datetime(2020, 1, 1, 12, 13, 14)), True, id='tz-same'
        ),
        pytest.param(
            datetime(2020, 1, 1, 12, 13, 14, tzinfo=timezone.utc),
            IsDatetime(approx=datetime(2020, 1, 1, 12, 13, 14), enforce_tz=False),
            True,
            id='tz-utc',
        ),
        pytest.param(
            datetime(2020, 1, 1, 12, 13, 14, tzinfo=timezone.utc),
            IsDatetime(approx=datetime(2020, 1, 1, 12, 13, 14)),
            False,
            id='tz-utc-different',
        ),
        pytest.param(
            datetime(2020, 1, 1, 12, 13, 14),
            IsDatetime(approx=datetime(2020, 1, 1, 12, 13, 14, tzinfo=timezone.utc), enforce_tz=False),
            False,
            id='tz-approx-tz',
        ),
        pytest.param(
            datetime(2020, 1, 1, 12, 13, 14, tzinfo=timezone(offset=timedelta(hours=1))),
            IsDatetime(approx=datetime(2020, 1, 1, 12, 13, 14), enforce_tz=False),
            True,
            id='tz-1-hour',
        ),
        pytest.param(
            pytz.timezone('Europe/London').localize(datetime(2022, 2, 15, 15, 15)),
            IsDatetime(
                approx=pytz.timezone('America/New_York').localize(datetime(2022, 2, 15, 10, 15)), enforce_tz=False
            ),
            True,
            id='tz-both-tz',
        ),
        pytest.param(
            pytz.timezone('Europe/London').localize(datetime(2022, 2, 15, 15, 15)),
            IsDatetime(approx=pytz.timezone('America/New_York').localize(datetime(2022, 2, 15, 10, 15))),
            False,
            id='tz-both-tz-different',
        ),
    ],
)
def test_is_datetime(value, is_dt, expect_match):
    if expect_match:
        assert value == is_dt
    else:
        assert value != is_dt


def test_is_now_dt():
    is_now = IsNow()
    dt = datetime.now()
    assert dt == is_now
    assert str(is_now) == repr(dt)


def test_is_now_str():
    assert datetime.now().isoformat() == IsNow(iso_string=True)


def test_repr():
    v = IsDatetime(approx=datetime(2032, 1, 2, 3, 4, 5), iso_string=True)
    assert str(v) == 'IsDatetime(approx=datetime.datetime(2032, 1, 2, 3, 4, 5), iso_string=True)'


def test_is_now_tz():
    now_ny = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(pytz.timezone('America/New_York'))
    assert now_ny == IsNow(tz='America/New_York')
    assert now_ny == IsNow(tz=timezone(timedelta(hours=-5)))


def test_delta():
    assert IsNow(delta=timedelta(hours=2)).delta == timedelta(seconds=7200)
    assert IsNow(delta=3600).delta == timedelta(seconds=3600)
    assert IsNow(delta=3600.1).delta == timedelta(seconds=3600, microseconds=100000)
