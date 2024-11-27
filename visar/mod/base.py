import string

from ..ar import Ar, Segment


def base_encode(value: int, charmap: str) -> str:
    if value == "0":
        return charmap[0]
    base = len(charmap)
    result = ""
    while value > 0:
        value, mod = divmod(value, base)
        result = charmap[mod] + result
    return result


BASE_HEX_36 = string.digits + string.ascii_lowercase
BASE_HEX_32 = BASE_HEX_36[:32]
BASE_HEX_64 = (BASE_HEX_36 + "!#$%&()*+,-_^./:;<=>?@[]~{|}")[:64]


def unicode_encode(value: int) -> str:
    pass


def p_int_b32(value: int) -> Segment:
    return "b32", "0_" + base_encode(value, BASE_HEX_32)


def p_int_b36(value: int) -> Segment:
    return "b36", "0_" + base_encode(value, BASE_HEX_36)


def p_int_b64(value: int) -> Segment:
    return "b64", "0 " + base_encode(value, BASE_HEX_64)


def enable(visar: Ar) -> None:
    visar.inject(
        int,
        p_int_b32,
        p_int_b36,
        p_int_b64,
    ).at_tail()
