import ast
from types import CodeType
from typing import Any

from .repl import Module, Namespace
from .vis import ar as visar

IDENT_QUERY = "q"


def init_query(ns: Namespace) -> None:
    ns.globals[IDENT_QUERY] = visar.resolve(None)

    from pathlib import Path

    ns.globals["Path"] = Path


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
    init=init_query,
    parser=lambda src: compile(src.lstrip(), "<input>", "eval"),
    executor=lambda code, ns: show(eval(code, *ns), ns),  # noqa: S307
)
mod_stmt = Module(
    parser=stmt_parser,
    executor=lambda data, ns: stmt_executor(*data, ns),
)
