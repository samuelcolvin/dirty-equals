from datetime import datetime, timedelta, tzinfo
from typing import Any, Optional, Union

from ._numeric import IsNumeric
from ._utils import Omit


class IsDatetime(IsNumeric[datetime]):
    types = datetime

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
    def __init__(
        self,
        delta: Union[timedelta, int, float] = 2,
        unix_number: bool = False,
        iso_string: bool = False,
        format_string: Optional[str] = None,
        enforce_tz: bool = True,
        tz: Union[None, str, tzinfo] = None,
    ):
        if isinstance(tz, str):
            import pytz

            tz = pytz.timezone(tz)

        if tz is not None:
            now = datetime.utcnow().astimezone(tz)
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
