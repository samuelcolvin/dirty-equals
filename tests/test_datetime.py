from datetime import datetime, timedelta, timezone

import pytest

from dirty_equals import IsNow, IsStr


def test_is_now_dt():
    is_now = IsNow()
    dt = datetime.now()
    assert dt == is_now
    assert str(is_now) == repr(dt)


def test_is_now_str():
    assert datetime.now().isoformat() == IsNow(iso_string=True)


def test_is_now_false():
    is_now = IsNow(iso_string=True)
    with pytest.raises(AssertionError):
        assert datetime(2000, 1, 1).strftime('%Y-%m-%dT%H:%M:%S') == is_now
    assert str(is_now) == IsStr(
        regex=r'IsNow\(approx=datetime.datetime\(\d+, \d+, \d+, \d+, \d+, \d+, \d+\), iso_string=True\)'
    )


def test_is_now_tz():
    diff = timedelta(hours=2)
    dt = datetime.now().replace(tzinfo=timezone(offset=diff)) + diff
    assert dt == IsNow()


# FIXME needs more tests for timezones, I don't trust the current logic
