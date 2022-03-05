from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Any, Optional, Union

from ._numeric import IsNumeric
from ._utils import Omit


class IsDatetime(IsNumeric[datetime]):
    """
    Check if the value is a datetime, and matches the given conditions.
    """

    allowed_types = datetime

    def __init__(
        self,
        *,
        approx: Optional[datetime] = None,
        delta: Optional[Union[timedelta, int, float]] = None,
        gt: Optional[datetime] = None,
        lt: Optional[datetime] = None,
        ge: Optional[datetime] = None,
        le: Optional[datetime] = None,
        unix_number: bool = False,
        iso_string: bool = False,
        format_string: Optional[str] = None,
        enforce_tz: bool = True,
    ):
        """
        Args:
            approx: A value to approximately compare to.
            delta: The allowable different when comparing to the value to `approx`, if omitted 2 seconds is used,
                ints and floats are assumed to represent seconds and converted to `timedelta`s.
            gt: Value which the compared value should be greater than (after).
            lt: Value which the compared value should be less than (before).
            ge: Value which the compared value should be greater than (after) or equal to.
            le: Value which the compared value should be less than (before) or equal to.
            unix_number: whether to allow unix timestamp numbers in comparison
            iso_string: whether to allow iso formatted strings in comparison
            format_string: if provided, `format_string` is used with `datetime.strptime` to parse strings
            enforce_tz: whether timezone should be enforced in comparison, see below for more details

        Examples of basic usage:

        ```py title="IsDatetime"
        from dirty_equals import IsDatetime
        from datetime import datetime

        y2k = datetime(2000, 1, 1)
        assert datetime(2000, 1, 1) == IsDatetime(approx=y2k)
        # Note: this requires the system timezone to be UTC
        assert 946684800.123 == IsDatetime(approx=y2k, unix_number=True)
        assert datetime(2000, 1, 1, 0, 0, 9) == IsDatetime(approx=y2k, delta=10)
        assert '2000-01-01T00:00' == IsDatetime(approx=y2k, iso_string=True)

        assert datetime(2000, 1, 2) == IsDatetime(gt=y2k)
        assert datetime(1999, 1, 2) != IsDatetime(gt=y2k)
        ```
        """
        if isinstance(delta, (int, float)):
            delta = timedelta(seconds=delta)

        super().__init__(
            approx=approx,
            delta=delta,  # type: ignore[arg-type]
            gt=gt,
            lt=lt,
            ge=ge,
            le=le,
        )
        self.unix_number = unix_number
        self.iso_string = iso_string
        self.format_string = format_string
        self.enforce_tz = enforce_tz
        self._repr_kwargs.update(
            unix_number=Omit if unix_number is False else unix_number,
            iso_string=Omit if iso_string is False else iso_string,
            format_string=Omit if format_string is None else format_string,
            enforce_tz=Omit if enforce_tz is True else format_string,
        )

    def prepare(self, other: Any) -> datetime:
        if isinstance(other, datetime):
            dt = other
        elif isinstance(other, (float, int)):
            if self.unix_number:
                dt = datetime.fromtimestamp(other)
            else:
                raise TypeError('numbers not allowed')
        elif isinstance(other, str):
            if self.iso_string:
                dt = datetime.fromisoformat(other)
            elif self.format_string:
                dt = datetime.strptime(other, self.format_string)
            else:
                raise ValueError('not a valid datetime string')
        else:
            raise ValueError(f'{type(other)} not valid as datetime')

        if self.approx is not None and not self.enforce_tz and self.approx.tzinfo is None and dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt

    def approx_equals(self, other: datetime, delta: timedelta) -> bool:
        if not super().approx_equals(other, delta):
            return False

        if self.enforce_tz:
            if self.approx.tzinfo is None:  # type: ignore[union-attr]
                return other.tzinfo is None
            else:
                approx_offset = self.approx.tzinfo.utcoffset(self.approx)  # type: ignore[union-attr]
                other_offset = other.tzinfo.utcoffset(other)  # type: ignore[union-attr]
                return approx_offset == other_offset
        else:
            return True


class IsNow(IsDatetime):
    """
    Check if a datetime is close to now, this is similar to `IsDatetime(approx=datetime.now())`,
    but slightly more powerful.
    """

    def __init__(
        self,
        *,
        delta: Union[timedelta, int, float] = 2,
        unix_number: bool = False,
        iso_string: bool = False,
        format_string: Optional[str] = None,
        enforce_tz: bool = True,
        tz: Union[None, str, tzinfo] = None,
    ):
        """
        Args:
            delta: The allowable different when comparing to the value to now, if omitted 2 seconds is used,
                ints and floats are assumed to represent seconds and converted to `timedelta`s.
            unix_number: whether to allow unix timestamp numbers in comparison
            iso_string: whether to allow iso formatted strings in comparison
            format_string: if provided, `format_string` is used with `datetime.strptime` to parse strings
            enforce_tz: whether timezone should be enforced in comparison, see below for more details
            tz: either a `pytz.timezone`, a `datetime.timezone` or a string which will be passed to `pytz.timezone`,
                if provided now will be converted to this timezone.

        ```py title="IsNow"
        from dirty_equals import IsNow
        from datetime import datetime, timezone

        now = datetime.now()
        assert now == IsNow
        assert now.timestamp() == IsNow(unix_number=True)
        assert now.timestamp() != IsNow
        assert now.isoformat() == IsNow(iso_string=True)
        assert now.isoformat() != IsNow

        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
        assert utc_now == IsNow(tz=timezone.utc)
        ```
        """
        if isinstance(tz, str):
            import pytz

            tz = pytz.timezone(tz)

        if tz is not None:
            now = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(tz)
        else:
            now = datetime.now()

        super().__init__(
            approx=now,
            delta=delta,
            unix_number=unix_number,
            iso_string=iso_string,
            format_string=format_string,
            enforce_tz=enforce_tz,
        )
        if tz is not None:
            self._repr_kwargs['tz'] = tz


class IsDate(IsNumeric[date]):
    """
    Check if the value is a date, and matches the given conditions.
    """

    allowed_types = date

    def __init__(
        self,
        *,
        approx: Optional[date] = None,
        delta: Optional[Union[timedelta, int, float]] = None,
        gt: Optional[date] = None,
        lt: Optional[date] = None,
        ge: Optional[date] = None,
        le: Optional[date] = None,
        iso_string: bool = False,
        format_string: Optional[str] = None,
    ):

        """
        Args:
            approx: A value to approximately compare to.
            delta: The allowable different when comparing to the value to now, if omitted 2 seconds is used,
                ints and floats are assumed to represent seconds and converted to `timedelta`s.
            gt: Value which the compared value should be greater than (after).
            lt: Value which the compared value should be less than (before).
            ge: Value which the compared value should be greater than (after) or equal to.
            le: Value which the compared value should be less than (before) or equal to.
            iso_string: whether to allow iso formatted strings in comparison
            format_string: if provided, `format_string` is used with `datetime.strptime` to parse strings

        Examples of basic usage:

        ```py title="IsDate"
        from dirty_equals import IsDate
        from datetime import date

        y2k = date(2000, 1, 1)
        assert date(2000, 1, 1) == IsDate(approx=y2k)
        assert '2000-01-01' == IsDate(approx=y2k, iso_string=True)

        assert date(2000, 1, 2) == IsDate(gt=y2k)
        assert date(1999, 1, 2) != IsDate(gt=y2k)
        ```
        """

        if delta is None:
            delta = timedelta()
        elif isinstance(delta, (int, float)):
            delta = timedelta(seconds=delta)

        super().__init__(approx=approx, gt=gt, lt=lt, ge=ge, le=le, delta=delta)  # type: ignore[arg-type]

        self.iso_string = iso_string
        self.format_string = format_string
        self._repr_kwargs.update(
            iso_string=Omit if iso_string is False else iso_string,
            format_string=Omit if format_string is None else format_string,
        )

    def prepare(self, other: Any) -> date:
        if type(other) is date:
            dt = other
        elif isinstance(other, str):
            if self.iso_string:
                dt = date.fromisoformat(other)
            elif self.format_string:
                dt = datetime.strptime(other, self.format_string).date()
            else:
                raise ValueError('not a valid date string')
        else:
            raise ValueError(f'{type(other)} not valid as date')

        return dt


class IsToday(IsDate):
    """
    Check if a date is today, this is similar to `IsDate(approx=date.today())`, but slightly more powerful.
    """

    def __init__(
        self,
        *,
        iso_string: bool = False,
        format_string: Optional[str] = None,
    ):
        """
        Args:
            iso_string: whether to allow iso formatted strings in comparison
            format_string: if provided, `format_string` is used with `datetime.strptime` to parse strings
        ```py title="IsToday"
        from dirty_equals import IsToday
        from datetime import date, timedelta

        today = date.today()
        assert today == IsToday
        assert today.isoformat() == IsToday(iso_string=True)
        assert today.isoformat() != IsToday
        assert today + timedelta(days=1) != IsToday
        assert today.strftime('%Y/%m/%d') == IsToday(format_string='%Y/%m/%d')
        assert today.strftime('%Y/%m/%d') != IsToday()
        ```
        """

        super().__init__(approx=date.today(), iso_string=iso_string, format_string=format_string)
