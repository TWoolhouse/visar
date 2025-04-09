import ast
from types import CodeType
from typing import Any

from .ar import Query
from .repl import Module, Namespace
from .vis import ar as visar

IDENT_QUERY = "q"
IDENT_QUERIES = "qs"
IDENTS_PINT_UREG = ["ureg", "unit", "u", "pint"]
IDENTS_PINT_QUANTITY = ["Q_", "Q"]

queries: list[Query] = []
query_objs: dict[int, Query] = {}


def init_query(ns: Namespace) -> None:
    query_from_object(None, ns)
    ns.locals.immutable[IDENT_QUERIES] = queries

    exec(  # noqa: S102
        r"""
from pathlib import Path
import itertools
import math
""",
        ns.globals,
        ns.locals.immutable,
    )


def init_pint(ns: Namespace) -> None:
    import pint

    ureg = pint.UnitRegistry(cache_folder=":auto:")
    ureg.formatter.default_format = "~#P"
    for ident in IDENTS_PINT_UREG:
        ns.globals[ident] = ureg
    for ident in IDENTS_PINT_QUANTITY:
        ns.globals[ident] = ureg.Quantity


def init_ns(ns: Namespace) -> None:
    init_query(ns)
    init_pint(ns)


def query_from_object(obj: Any, ns: Namespace) -> Query:
    if (query := query_objs.get(id(obj))) is not None:
        ns.locals.immutable[IDENT_QUERY] = query
        return query

    query = visar.resolve(obj)
    query._update({IDENT_QUERIES: (len(queries), None)})

    queries.append(query)
    query_objs[id(query)] = query

    ns.locals.immutable[IDENT_QUERIES] = queries
    ns.locals.immutable[IDENT_QUERY] = query

    return query


def show(value: Any, ns: Namespace) -> None:
    return visar.show(query_from_object(value, ns))


def stmt_parser(src: str) -> tuple[ast.Interactive, CodeType]:
    tree = ast.parse(src.lstrip(), "<input>", "single")
    code = compile(tree, "<input>", "single")
    return tree, code


def stmt_executor(tree: ast.Interactive, code: CodeType, ns: Namespace) -> None:
    exec(code, *ns)  # noqa: S102
    stmt = tree.body[0]
    if isinstance(stmt, ast.Assign) and isinstance(name := stmt.targets[0], ast.Name):
        show(ns[name.id], ns)


mod_expr = Module(
    init=lambda _ns: init_ns,  # async loading
    parser=lambda src: compile(src.lstrip(), "<input>", "eval"),
    executor=lambda code, ns: show(eval(code, *ns), ns),  # noqa: S307
)
mod_stmt = Module(
    # init is inheritted
    parser=stmt_parser,
    executor=lambda data, ns: stmt_executor(*data, ns),
)
