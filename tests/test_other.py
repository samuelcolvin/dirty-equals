import uuid

import pytest

from dirty_equals import IsUUID


def test_is_uuid_true():
    is_uuid = IsUUID()
    uuid_ = uuid.uuid4()
    assert uuid_ == is_uuid
    assert str(is_uuid) == repr(uuid_)


def test_is_uuid_false():
    is_uuid = IsUUID()
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(*)'


def test_is_uuid4_false():
    is_uuid = IsUUID(4)
    with pytest.raises(AssertionError):
        assert '123' == is_uuid
    assert str(is_uuid) == 'IsUUID(4)'
