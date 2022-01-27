from datetime import datetime, timedelta, timezone
from typing import Any, Union

from ._numeric import IsNumeric
from ._utils import Omit


class IsDatetime(IsNumeric[datetime]):
    types = datetime

    def __init__(
        self,
        *,
        approx: datetime = None,
        delta: Union[timedelta, int] = None,
        gt: datetime = None,
        lt: datetime = None,
        ge: datetime = None,
        le: datetime = None,
        unix_number: bool = False,
        iso_string: bool = False,
        format_string: str = None,
        tz: Union[str, timezone] = None,  # TODO checks
    ):
        if isinstance(delta, int):
            delta = timedelta(seconds=delta)
        self.delta = delta
        super().__init__(approx=approx, gt=gt, lt=lt, ge=ge, le=le)
        self.unix_number = unix_number
        self.iso_string = iso_string
        self.format_string = format_string
        self.tz = tz
        self._repr_kwargs.update(
            unix_number=unix_number or Omit,
            iso_string=iso_string or Omit,
            format_string=format_string or Omit,
            tz=tz or Omit,
        )

    def prepare(self, other: Any) -> datetime:
        if isinstance(other, datetime):
            dt = other
        elif isinstance(other, float):
            if self.unix_number:
                dt = datetime.fromtimestamp(other)
            else:
                raise TypeError('floats not allowed')
        elif isinstance(other, str):
            if self.iso_string:
                dt = datetime.fromisoformat(other)
            elif self.format_string:
                dt = datetime.strptime(other, self.format_string)
            else:
                raise ValueError('not a valid datetime string')
        else:
            raise ValueError(f'{type(other)} not valid as datetime')

        if dt.tzinfo:
            self.approx = self.approx.replace(tzinfo=timezone.utc)
        return dt


class IsNow(IsDatetime):
    def __init__(
        self,
        delta: Union[timedelta, int] = 2,
        unix_number: bool = False,
        iso_string: bool = False,
        format_string: str = None,
        tz: Union[str, timezone] = None,  # TODO checks
    ):
        super().__init__(
            approx=datetime.now(),
            delta=delta,
            unix_number=unix_number,
            iso_string=iso_string,
            format_string=format_string,
            tz=tz,
        )

    # def prepare(self, other: Any) -> datetime:
    #     other = super().prepare(other)
    #
