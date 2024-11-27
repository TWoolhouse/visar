import traceback
from dataclasses import dataclass
from typing import Any, Callable, Iterator


class Namespace:
    def __init__(self) -> None:
        self.globals = {}
        self.locals = {}

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter((self.globals, self.locals))

    def __getitem__(self, key: str) -> Any:
        try:
            return self.locals[key]
        except KeyError:
            return self.globals[key]


def print_exc(exc: BaseException, frames: int = 0) -> None:
    tb = exc.__traceback__
    traceback.print_exception(type(exc), exc, tb, limit=-frames)


type Parser[T] = Callable[[str], T]
type Executor[T] = Callable[[T, Namespace], None]
type Init = Callable[[Namespace], None]


@dataclass(frozen=True, kw_only=True, slots=True)
class Module[T]:
    init: Init = lambda *_: None
    parser: Parser[T]
    executor: Executor[T]


def _parse[T](src: str, modules: list[Module]) -> tuple[T, Module[T]]:
    syn_exc: SyntaxError | None = None
    for module in modules:
        try:
            return module.parser(src), module
        except SyntaxError as exc:
            syn_exc = exc

    if syn_exc is None:
        raise ValueError("No modules!")
    raise syn_exc


def main(modules: list[Module], input_: Callable[[], str]) -> None:
    ns = Namespace()

    for module in modules:
        module.init(ns)

    while True:
        try:
            line = input_()
        except EOFError:
            # Gracefully quit on EOF
            break

        # Skip blank inputs
        if not line.strip():
            continue

        # Find a module that can parse the input
        try:
            code, module = _parse(line, modules)
        except SyntaxError as exc:
            print_exc(exc, frames=1)
            continue

        # Execute
        try:
            module.executor(code, ns)
        except Exception as exc:
            print_exc(exc, frames=1)
            continue
