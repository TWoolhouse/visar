import pint

from ..ar import Ar, Segment, g_instance, n_into


def g_mag(v: pint.Quantity) -> float:
    return float(v.magnitude)


def p_dimensions(v: pint.Quantity) -> Segment:
    return "unit", f"{v.units:D}"


def p_dimensions_base(v: pint.Quantity) -> Segment:
    return "SI", f"{v.to_base_units().units:D}"


def enable(visar: Ar) -> None:
    visar.register(
        pint.Quantity,
        (g_instance(pint.Quantity), [p_dimensions, p_dimensions_base, n_into(g_mag, visar[float])]),
    ).inject(visar.special.any).at_tail()
