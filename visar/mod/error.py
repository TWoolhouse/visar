import errno
import os
from pathlib import Path

from ..ar import Ar, Segment


def p_errno_value(value: int) -> Segment:
    key = abs(value)
    if (code := errno.errorcode.get(key)) is None:
        return None
    return "errno", f"{code} - {os.strerror(key)}"


def p_errno_name(name: str) -> Segment:
    name = name.upper().strip()
    for key in (name, f"E{name}"):
        try:
            value = getattr(errno, key)
            return "errno", f"{value} - {key} - {os.strerror(value)}"
        except AttributeError:
            continue
    return None


def enable(visar: Ar) -> None:
    visar.inject(
        int,
        p_errno_value,
    ).at_tail()

    visar.inject(
        str,
        p_errno_name,
    ).at_tail()
