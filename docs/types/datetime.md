# Date and Time Types

::: dirty_equals.IsDatetime

### Timezones

Timezones are hard, anyone who claims otherwise is either a genius, a liar, or an idiot.

`IsDatetime` and its subtypes (e.g. [`IsNow`][dirty_equals.IsNow]) can be used in two modes,
based on the `enforce_tz` parameter:

* `enforce_tz=True` (the default):
    * if the datetime wrapped by `IsDatetime` is timezone naive, the compared value must also be timezone naive.
    * if the datetime wrapped by `IsDatetime` has a timezone, the compared value must have a
      timezone with the same offset.
* `enforce_tz=False`:
    * if the datetime wrapped by `IsDatetime` is timezone naive, the compared value can either be naive or have a
      timezone all that matters is the datetime values match.
    * if the datetime wrapped by `IsDatetime` has a timezone, the compared value needs to represent the same point in
      time - either way it must have a timezone.

Example

```py
title="IsDatetime & timezones"
from datetime import datetime

from dirty_equals import IsDatetime
import pytz

tz_london = pytz.timezone('Europe/London')
new_year_london = tz_london.localize(datetime(2000, 1, 1))

tz_nyc = pytz.timezone('America/New_York')
new_year_eve_nyc = tz_nyc.localize(datetime(1999, 12, 31, 19, 0, 0))

assert new_year_eve_nyc == IsDatetime(approx=new_year_london, enforce_tz=False)
assert new_year_eve_nyc != IsDatetime(approx=new_year_london, enforce_tz=True)

new_year_naive = datetime(2000, 1, 1)

assert new_year_naive != IsDatetime(approx=new_year_london, enforce_tz=False)
assert new_year_naive != IsDatetime(approx=new_year_eve_nyc, enforce_tz=False)
assert new_year_london == IsDatetime(approx=new_year_naive, enforce_tz=False)
assert new_year_eve_nyc != IsDatetime(approx=new_year_naive, enforce_tz=False)
```

::: dirty_equals.IsNow

::: dirty_equals.IsDate

::: dirty_equals.IsToday
