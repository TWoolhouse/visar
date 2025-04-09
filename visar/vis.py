from collections.abc import Callable

from .ar import Ar, Gate, Graph, Node, Printer, Segment, g_always, g_instance, n_into, p_identity

type Module = Callable[[Ar], None]

__all__ = [
    "Ar",
    "ar",
    "Gate",
    "Graph",
    "Module",
    "Node",
    "Printer",
    "Segment",
    "g_always",
    "g_instance",
    "n_into",
    "p_identity",
]

ar = Ar()


def enable(*modules: Module) -> None:
    ar.module(*modules)
