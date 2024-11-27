from typing import Callable

from .ar import Ar, Gate, Graph, Node, Printer, Segment, g_always, g_instance, n_into, p_identity

__all__ = ["Ar", "ar", "Gate", "Graph", "Node", "Printer", "Segment", "g_always", "g_instance", "n_into", "p_identity"]

ar = Ar()


def enable(*modules: Callable[[Ar], None]) -> None:
    ar.module(*modules)