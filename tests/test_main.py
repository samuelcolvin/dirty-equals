import uuid
from datetime import datetime, timedelta, timezone

import pytest
from pytest_toolbox.comparison import AnyInt, CloseToNow, IsUUID, RegexStr


def test_close_to_now_true():
    c2n = CloseToNow()
    dt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    assert dt == c2n
    assert str(c2n) == repr(dt)


def test_close_to_now_true_dt():
    assert datetime.utcnow() == CloseToNow()


def test_close_to_now_false():
    c2n = CloseToNow()
    with pytest.raises(AssertionError):
        assert datetime(2000, 1, 1).strftime('%Y-%m-%dT%H:%M:%S') == c2n
    assert str(c2n).startswith('<CloseToNow(delta=2, now=')


def test_clow_to_now_tz():
    diff = timedelta(hours=2)
    dt = datetime.utcnow().replace(tzinfo=timezone(offset=diff)) + diff
    assert dt == CloseToNow()


def test_any_int_true():
    any_int = AnyInt()
    assert 123 == any_int
    assert str(any_int) == '123'


def test_any_int_false():
    any_int = AnyInt()
    with pytest.raises(AssertionError):
        assert '123' == any_int
    assert str(any_int) == '<AnyInt>'


def test_regex_true():
    assert 'whatever' == RegexStr('whatever')
    reg = RegexStr('wh.*er')
    assert 'whatever' == reg
    assert str(reg) == "'whatever'"


def test_regex_false():
    reg = RegexStr('wh.*er')
    with pytest.raises(AssertionError):
        assert 'WHATEVER' == reg
    assert str(reg) == "<RegexStr(regex=re.compile('wh.*er', re.DOTALL)>"


def test_is_uuid_true():
    is_uuid = IsUUID()
    uuid_ = uuid.uuid4()
    assert uuid_ == is_uuid
    assert str(is_uuid) == repr(uuid_)


def test_is_uuid_false():
    is_uuid = IsUUID()
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == '<UUID(*)>'
