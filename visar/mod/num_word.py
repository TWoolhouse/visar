import functools

from ..ar import Ar, Segment

unit = {
    0: "",
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
    8: "eight",
    9: "nine",
}

teens = {
    11: "eleven",
    12: "twelve",
    13: "thirteen",
    14: "fourteen",
    15: "fifteen",
    16: "sixteen",
    17: "seventeen",
    18: "eighteen",
    19: "nineteen",
}

tees = (
    (20, "twenty"),
    (30, "thirty"),
    (40, "forty"),
    (50, "fifty"),
    (60, "sixty"),
    (70, "seventy"),
    (80, "eighty"),
    (90, "ninety"),
)


under_100_above_19 = {
    (ten_value + unit_value): (f"{ten_name}{"-" if unit_value else ""}{unit_name}")
    for ten_value, ten_name in tees
    for unit_value, unit_name in unit.items()
}

under_100 = {**unit, **teens, **under_100_above_19, **{0: "zero", 10: "ten"}}
hundreds = {i * 100: f"{unit[i]} hundred" for i in range(1, 10)}

under_1_000_above_100 = {
    (hv + uv): (hn + un)
    for hv, hn in hundreds.items()
    for uv, un in ((v, f" and {n}" if v else "") for v, n in under_100.items())
}

under_1000 = {**under_100, **under_1_000_above_100}

factors = ["thousand", "million", "billion", "trillion", "quadrillion", "quintillion"]


@functools.lru_cache
def whole_number(value: int) -> str:
    big, small = divmod(value, 1000)

    buffer = []
    for factor in factors:
        if not big:
            break
        l = big % 1000
        if l:
            buffer.append(f"{under_1000[l]} {factor}")
        big //= 1000

    top = " ".join(reversed(buffer))

    if not small:
        if top:
            return top
        return under_1000[small]

    bot = under_1000[small]
    if top:
        return f"{top}{" " if "and" in bot else " and "}{bot}"
    return bot


def number_into_words(value: float) -> str:
    if value < 0:
        value = abs(value)
        neg = "negative "
    else:
        neg = ""
    whole = int(value)
    # decimal = value % 1

    return neg + whole_number(whole)


def p_words(value: float) -> Segment:
    return "number", number_into_words(value)


def enable(visar: Ar) -> None:
    visar.inject(
        float,
        p_words,
    ).at_tail()
