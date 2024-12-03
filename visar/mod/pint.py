import pint

from ..ar import Ar, Segment, g_instance, n_into


def g_mag(v: pint.Quantity) -> float:
    return float(v.magnitude)


def g_dimensions(v: pint.Quantity) -> Segment:
    return "SI", f"{v.units:D}"


def g_dimensions_base(v: pint.Quantity) -> Segment:
    return "SI Base", f"{v.to_base_units().units:D}"


def enable(visar: Ar) -> None:
    visar.register(
        pint.Quantity,
        (g_instance(pint.Quantity), [g_dimensions, n_into(g_mag, visar[float])]),
    ).inject(visar.special.any).at_tail()
