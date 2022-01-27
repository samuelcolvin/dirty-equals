# import uuid
# from datetime import datetime, timedelta, timezone
#
# import pytest
#
# from dirty_equals import AnyInt, CloseToNow, IsUUID, RegexStr


# def test_close_to_now_true():
#     c2n = CloseToNow()
#     dt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
#     assert dt == c2n
#     assert str(c2n) == repr(dt)
#
#
# def test_close_to_now_true_dt():
#     assert datetime.utcnow() == CloseToNow()
#
#
# def test_close_to_now_false():
#     c2n = CloseToNow()
#     with pytest.raises(AssertionError):
#         assert datetime(2000, 1, 1).strftime('%Y-%m-%dT%H:%M:%S') == c2n
#     assert str(c2n).startswith('<CloseToNow(delta=2, now=')
#
#
# def test_clow_to_now_tz():
#     diff = timedelta(hours=2)
#     dt = datetime.utcnow().replace(tzinfo=timezone(offset=diff)) + diff
#     assert dt == CloseToNow()
