import argparse
import os
import shlex
from collections.abc import Callable
from pprint import pp
from typing import NoReturn

from . import py as mod_py
from .memoize import memoize
from .repl import Module, Namespace


class ArgumentParser(argparse.ArgumentParser):
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        raise argparse.ArgumentError(None, f"EXIT-{status} {message}")

    def error(self, message: str) -> NoReturn:
        raise SyntaxError(message)


type Main = Callable[[argparse.Namespace, Namespace], None]


def set_main(parser: argparse.ArgumentParser, func: Main) -> None:
    parser.set_defaults(exec_main=func)


def main_introspection_namespace(args: argparse.Namespace, ns: Namespace) -> None:
    pp(ns.locals.immutable if args.globals else ns.locals.mutable, width=180, sort_dicts=True, underscore_numbers=True)
    if args.clear:
        print(f"Destroying {len(ns.locals.mutable)} entries")
        ns.locals.mutable.clear()


def main_stringify(args: argparse.Namespace, ns: Namespace) -> None:
    mod_py.show(" ".join(args.rest), ns)


def main_clear(_args: argparse.Namespace, _ns: Namespace) -> None:
    os.system("cls" if os.name == "nt" else "clear")  # noqa: S605


@memoize
def cli() -> ArgumentParser:
    parser = ArgumentParser("visar", exit_on_error=False)

    parser_cmds = parser.add_subparsers(required=True)
    parser_introspection = parser_cmds.add_parser(
        "introspection",
        aliases=["intro"],
        help="Inspect the current session",
        exit_on_error=False,
    )

    parser_introspection_cmds = parser_introspection.add_subparsers(required=True)
    parser_introspection_ns = parser_introspection_cmds.add_parser(
        "namespace",
        aliases=["ns"],
        help="Display the repl's namespace",
        exit_on_error=False,
    )
    parser_introspection_ns.add_argument(
        "-c", "--clear", action="store_true", default=False, help="Destroy the local namespace after displaying it."
    )
    parser_introspection_ns.add_argument(
        "-g", "--globals", action="store_true", default=False, help="Display the global scope."
    )
    set_main(parser_introspection_ns, main_introspection_namespace)

    parser_stringify = parser_cmds.add_parser(
        "string",
        aliases=["str"],
        help="Interpret the following arguments as a string and visar it.",
        exit_on_error=False,
    )
    parser_stringify.add_argument("rest", nargs="*")
    set_main(parser_stringify, main_stringify)

    parser_clear = parser_cmds.add_parser(
        "clear",
        aliases=["cls"],
        help="Clear the terminal.",
        exit_on_error=False,
    )
    set_main(parser_clear, main_clear)

    return parser


def parse(src: str) -> argparse.Namespace | None:
    try:
        args = shlex.split(src)
        ns = cli().parse_args(args)
    except argparse.ArgumentError as exc:
        if exc.message.startswith("EXIT-"):
            return None
        raise SyntaxError from exc
    except ValueError as exc:
        raise SyntaxError from exc
    return ns


def execute(args: argparse.Namespace | None, ns: Namespace) -> None:
    if args is None:
        return
    main: Main = args.exec_main
    main(args, ns)


mod_cmd = Module(
    parser=parse,
    executor=execute,
)
