import csv
from dataclasses import dataclass
from pathlib import Path

from ..ar import Ar, Segment, g_instance, n_into
from ..memoize import memoize


@dataclass(slots=True, kw_only=True)
class Element:
    name: str
    symbol: str
    atomic_number: int
    standard_weight: float


@dataclass(slots=True)
class PeriodicTable:
    elements: list[Element]
    by_symbol: dict[str, Element]
    by_name: dict[str, Element]


def _parse_elements() -> list[Element]:
    with (Path(__file__).parent.parent / "res/elements.csv").open() as f:
        f.readline()  # Skip header
        return [
            Element(
                name=e[2],
                symbol=e[1],
                atomic_number=int(e[0]),
                standard_weight=float(e[6]),
            )
            for e in csv.reader(f)
        ]


@memoize
def elements() -> PeriodicTable:
    elements = _parse_elements()

    return PeriodicTable(
        elements,
        {e.symbol: e for e in elements},
        {e.name.lower(): e for e in elements},
    )


def g_element_from_atomic_number(atomic_number: int) -> Element:
    if atomic_number > 0:
        return elements().elements[atomic_number - 1]
    raise ValueError("Invalid atomic number")


def g_element_from_name(name: str) -> Element:
    return elements().by_name[name.lower().strip()]


def g_element_from_symbol(symbol: str) -> Element:
    return elements().by_symbol[symbol.strip()]


def p_element(e: Element) -> Segment:
    return "element", e, f"{e.symbol}({e.atomic_number}) {e.name} ≈ {e.standard_weight}u"


def enable(visar: Ar) -> None:
    elements()  # Load elements

    visar.register(
        Element,
        (g_instance(Element), [p_element, n_into(lambda e: e.atomic_number, visar[int])]),
    ).inject(visar.special.any).at_tail()

    visar.inject(
        int,
        n_into(g_element_from_atomic_number, visar[Element]),
    ).at_tail()

    visar.inject(
        str,
        n_into(g_element_from_name, visar[Element]),
        n_into(g_element_from_symbol, visar[Element]),
    ).at_head()
