from collections.abc import Iterable, Iterator
from fractions import Fraction
from typing import Any, cast

from ..ar import Ar, Segment, g_always, g_instance, n_into, p_identity

# --- all


def p_type(value: Any) -> Segment:
    t = type(value)
    return "type", t, f"{t.__module__}.{t.__qualname__}"


# --- str


def p_str_len(v: str) -> Segment:
    return "chars", len(v)


def p_str_words(v: str) -> Segment:
    return "words", len(v.split())


# --- chr


def g_chr(v: str) -> str:
    if len(v) != 1:
        raise ValueError
    return g_instance(str)(v)


# --- int


def p_int_bin(v: int) -> Segment:
    return "bin", f"0b{v:_b}"


def p_int_oct(v: int) -> Segment:
    return "oct", f"0o{v:_o}"


def p_int_dec(v: int) -> Segment:
    return "dec", f"0d{v:_}"


def p_int_hex(v: int) -> Segment:
    return "hex", f"0x{v:_x}"


# --- float


def g_fractional(v: float) -> float:
    if v.is_integer():
        raise ValueError("Must be float")
    return v


def p_fraction(v: float) -> Segment:
    nu, de = v.as_integer_ratio()
    return "Frac", Fraction(nu, de), f"{nu}/{de}"


def g_int(v: float) -> int:
    if v.is_integer():
        return int(v)
    raise ValueError


# --- iterables


def g_iterable(v: Any) -> Iterable:
    if isinstance(v, Iterable) and not isinstance(v, Iterator):
        return v
    raise ValueError


def p_iterable_len(v: Iterable) -> Segment:
    return "len", sum(1 for _ in v)


# --- enable


def enable(visar: Ar) -> None:
    visar.register(
        visar.special.all,
        (g_always, [p_identity, p_type]),
    ).inject(visar.special.any).at_head()

    visar.register(
        int,
        (g_instance(int), [p_int_bin, p_int_oct, p_int_dec, p_int_hex]),
    )

    visar.register(
        float,
        (g_instance(float), [n_into(g_int, visar[int]), (g_fractional, [p_fraction])]),
    ).inject(visar.special.any).at_tail()

    visar.register(
        str,
        (g_instance(str), [p_str_len, p_str_words]),
    ).inject(visar.special.any).at_tail()

    visar.register(
        chr,
        (g_chr, [n_into(lambda x: float(ord(cast(str, x))), visar[float])]),
    )

    visar.register(
        Iterable,
        (g_iterable, [p_iterable_len]),
    )

    visar.inject(
        str,
        n_into(float, visar[float]),
        n_into(g_always, visar[chr]),
    ).at_tail()

    visar.register(
        visar.special.convert,
        (g_always, [visar[Iterable], n_into(float, visar[float]), n_into(str, visar[str])]),
    ).inject(visar.special.any).at_tail()
