import ast
from types import CodeType
from typing import Any

from .repl import Module, Namespace
from .vis import ar as visar

IDENT_QUERY = "q"
IDENTS_PINT_UREG = ["ureg", "unit", "u"]
IDENTS_PINT_QUANTITY = ["Q_", "Q"]


def init_query(ns: Namespace) -> None:
    ns.globals[IDENT_QUERY] = visar.resolve(None)

    from pathlib import Path

    ns.globals["Path"] = Path


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


def show(value: Any, ns: Namespace) -> None:
    query = ns.globals[IDENT_QUERY]
    if value is not query:
        query = visar.resolve(value)
        ns.globals[IDENT_QUERY] = query
    return visar.show(query)


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
    init=lambda ns: init_ns,
    parser=lambda src: compile(src.lstrip(), "<input>", "eval"),
    executor=lambda code, ns: show(eval(code, *ns), ns),  # noqa: S307
)
mod_stmt = Module(
    # init is inheritted
    parser=stmt_parser,
    executor=lambda data, ns: stmt_executor(*data, ns),
)
