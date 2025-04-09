import pint

from ..ar import Ar, Segment, g_instance, n_into


def g_mag(v: pint.Quantity) -> float:
    return float(v.magnitude)


def p_given(u: pint.Quantity) -> Segment:
    return "quantity", u, f"{u:D}"


def p_dimensions(u: pint.Unit) -> Segment:
    return "dim", u.dimensionality


def p_unit_si(u: pint.Unit) -> Segment:
    units = (1 * u).to_base_units().units
    return "SI", units, f"{units:D}"


def g_unit(v: pint.Quantity) -> pint.Unit:
    return v.units


def enable(visar: Ar) -> None:
    visar.register(
        pint.Unit,
        (g_instance(pint.Unit), [p_unit_si, p_dimensions]),
    ).inject(visar.special.any).at_tail()

    visar.register(
        pint.Quantity,
        (g_instance(pint.Quantity), [p_given, n_into(g_unit, visar[pint.Unit]), n_into(g_mag, visar[float])]),
    ).inject(visar.special.any).at_tail()
