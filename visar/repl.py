import itertools
import threading
import traceback
from collections.abc import Callable, Iterator, MutableMapping
from dataclasses import dataclass
from typing import Any


class Namespace:
    class Frozen(MutableMapping[str, Any]):
        def __init__(self) -> None:
            self.immutable = {}
            self.mutable = {}

        def __getitem__(self, key: str) -> Any:
            try:
                return self.mutable[key]
            except KeyError as exc:
                return self.immutable[key]

        def __setitem__(self, key: str, value: Any) -> None:
            self.mutable[key] = value

        def __contains__(self, key: object) -> bool:
            return key in self.mutable or key in self.immutable

        def __delitem__(self, key: str) -> None:
            del self.mutable[key]

        def __iter__(self) -> Iterator[str]:
            return itertools.chain(self.mutable, self.immutable)

        def __len__(self) -> int:
            return len(self.mutable) + len(self.immutable)

    def __init__(self) -> None:
        self.globals = {}
        self.locals = self.Frozen()

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


type Defer = Callable[[Namespace], Any]
type Parser[T] = Callable[[str], T]
type Executor[T] = Callable[[T, Namespace], None]
type Init = Callable[[Namespace], None | Defer]


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


def main(modules: list[Module], input_: Callable[[], str], defer: Defer) -> None:
    ns = Namespace()
    deferred = [defer]

    for module in modules:
        res = module.init(ns)
        if res is not None:
            deferred.append(res)

    defer_done = threading.Event()
    threading.Thread(target=lambda: ([d(ns) for d in deferred], defer_done.set())).start()

    while True:
        try:
            line = input_()
        except EOFError:
            # Gracefully quit on EOF
            break

        # Skip blank inputs
        if not line.strip():
            continue

        # Wait for all deferred tasks to finish
        defer_done.wait()

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
