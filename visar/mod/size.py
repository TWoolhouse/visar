import math

from ..ar import Ar, Segment


def int_byte_size(value: int, metric: bool) -> str:
    shift = 1000 if metric else 1024
    v = float(value)
    SI = ["", "K", "M", "G", "T", "P"]
    for i, _si in enumerate(SI):
        if abs(v / (shift**i)) < 1:
            i = max(i - 1, 0)
            break
    if not metric and SI[i]:
        SI[i] += "i"
    return f"{v / (shift**i):_.3f} {SI[i]}B"


def p_int_byte_size(value: int) -> Segment:
    return "size", f"{int_byte_size(value, True)} {int_byte_size(value, False)}"


def p_log2(value: float) -> Segment:
    try:
        return "log2", f"{math.log2(value):.3f}"
    except ValueError:
        return "log2", float("nan")


def p_log10(value: float) -> Segment:
    try:
        return "log10", f"{math.log10(value):.3f}"
    except ValueError:
        return "log10", float("nan")


def p_pages_4k(value: float) -> Segment:
    return "pages<4k>", math.ceil(abs(value) / 0x1000)


def enable(visar: Ar) -> None:
    visar.inject(
        int,
        p_int_byte_size,
    ).at_tail()

    visar.inject(
        float,
        p_log2,
        p_log10,
        p_pages_4k,
    ).at_tail()
