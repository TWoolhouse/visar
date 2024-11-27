import contextlib
import datetime

import zoneinfo

from ..ar import Ar, Segment, g_instance, n_into


def _get_timezone() -> zoneinfo.ZoneInfo | datetime.timezone:
    try:
        return zoneinfo.ZoneInfo("Europe/London")
    except zoneinfo.ZoneInfoNotFoundError:
        return datetime.UTC


TZ_LONDON = _get_timezone()


def g_timedelta(v: int) -> datetime.timedelta:
    return datetime.timedelta(seconds=v)


def p_time_delta(delta: datetime.timedelta) -> Segment:
    sec = delta.total_seconds()
    if sec >= 0:
        return "time", f"+{delta}"
    return "time", f"-{datetime.timedelta(seconds=abs(sec))}"


def p_time_from_now(delta: datetime.timedelta) -> Segment:
    now = datetime.datetime.now(TZ_LONDON)
    with contextlib.suppress(OverflowError):
        return "now+", now + delta


def enable(visar: Ar) -> None:
    visar.register(
        datetime.timedelta,
        (g_instance(datetime.timedelta), [p_time_delta, p_time_from_now]),
    )

    visar.inject(
        float,
        n_into(g_timedelta, visar[datetime.timedelta]),
    ).at_tail()
