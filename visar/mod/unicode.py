import unicodedata

from ..ar import Ar, Segment


def p_unicode_point(value: int) -> Segment:
    if value not in range(0x110000):
        return None
    char = chr(value)
    return "unicode", f"{unicodedata.category(char)} {unicodedata.name(char, "<nameless>")} \"{char}\""


def enable(visar: Ar) -> None:
    visar.inject(
        int,
        p_unicode_point,
    ).at_tail()
