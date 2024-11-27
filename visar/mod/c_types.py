from ..ar import Ar, Segment


def type_ints(value: int, allow_unsigned: bool) -> str:
    types: dict[str, tuple[int, int]] = {
        **{f"u{bits}": (0, 2**bits) for bits in (8, 16, 32, 64, 128, 256, 512, 1014)},
        **{f"i{bits}": (-(2**bits), 2**bits - 1) for bits in (8, 16, 32, 64, 128, 256, 512, 1024)},
    }
    if value < 0:
        for name, mn in sorted(
            ((n, mn) for n, (mn, _) in types.items()),
            key=lambda x: x[1],
            reverse=True,
        ):
            if mn <= value:
                return name
    elif not allow_unsigned:
        for name, mx in sorted(
            ((n, mx) for n, (mn, mx) in types.items() if mn != 0),
            key=lambda x: x[1],
        ):
            if value < mx:
                return name
    else:
        for name, mx in sorted(
            ((n, mx) for n, (mn, mx) in types.items() if mn == 0),
            key=lambda x: x[1],
        ):
            if value < mx:
                return name
    raise RuntimeError("Unreachable")


def p_ctypes_ints(value: int) -> Segment:
    buffer = f"{type_ints(value, True)}"
    if value >= 0:
        buffer += f" {type_ints(value, False)}"
    return "ctype", buffer


def enable(visar: Ar) -> None:
    visar.inject(
        int,
        p_ctypes_ints,
    ).at_tail()
