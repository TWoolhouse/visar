from typing import Any, Callable, Iterator, Reversible, Self, Sequence

type Seg[T] = tuple[str, T]
type Segment[T] = Seg[T] | None
type Gate[From, Into] = Callable[[From], Into]
type Printer[T] = Callable[[T], Segment]

type Branch[From, Into] = tuple[Gate[From, Into], Sequence[Branch[Into, Any] | Printer[Into]]]
type Node[T] = Branch[T, Any] | Printer[T]
type Graph[T] = list[Branch[T, Any]]


def _resolve_node(branch: Branch, value: Any, done: set[int]) -> Iterator[Seg]:
    # No duplicates if run successfully!
    if id(branch) in done:
        return

    gate, children = branch
    try:
        new = gate(value)
    except Exception:  # noqa: S112
        return
    done.add(id(branch))
    for child in children:
        if isinstance(child, tuple):
            yield from _resolve_node(child, new, done)
        else:
            seg = child(new)
            if seg is not None:
                yield seg


def resolve_graph[T](graph: Graph[T], value: T) -> Iterator[Seg]:
    done = set()
    for branch in graph:
        yield from _resolve_node(branch, value, done)


class inject[T]:
    def __init__(self, _into: Sequence[Node[T]], nodes: Reversible[Node[T]]) -> None:
        self._root: list[Node[T]] = _into  # type: ignore
        self._nodes = nodes
        self.__used = False

    def __use(self) -> None:
        if self.__used:
            raise RuntimeError("Already Injected!")
        self.__used = True

    def __del__(self) -> None:
        if not self.__used:
            raise RuntimeError("Injection not used!")

    @classmethod
    def into_graph(cls, graph: Graph[T], *nodes: Node[T]) -> Self:
        return cls(graph, nodes)

    @classmethod
    def into_branch(cls, branch: Branch[T, Any], *nodes: Node[T]) -> Self:
        return cls(branch[1], nodes)

    def at_head(self) -> None:
        self.__use()
        for node in reversed(self._nodes):
            self._root.insert(0, node)

    def at_tail(self) -> None:
        self.__use()
        self._root.extend(self._nodes)


type Ty = Any


class Query:
    __aliases = {
        "self": "=",
    }

    def __init__(self, graph: Graph, value: Any) -> None:
        self.__value = value
        self.__segments: dict[str, Any] = dict(resolve_graph(graph, value))

    def _show(self) -> None:
        length = max(len(k) for k in self.__segments)

        for key, value in self.__segments.items():
            print(f"{key:>{length}} {value}")
        print()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.__value})"

    def __getitem__(self, key: str) -> Any:
        try:
            return self.__segments[key]
        except KeyError:
            return self.__segments[self.__aliases[key]]

    def __getattr__(self, name: str) -> Any:
        return self.__getitem__(name)


class Ar:
    """Argument Registry"""

    class special:
        any = type("any", (), {})
        all = type("all", (), {})
        convert = type("convert", (), {})

    class Registration[B: Branch]:
        def __init__(self, ar: "Ar", _t: Ty, b: B) -> None:
            self.__ar = ar
            self.branch = b

        def inject(self, within: Ty) -> inject:
            return self.__ar.inject(within, self.branch)

    def __init__(self) -> None:
        self.registry: dict[Ty, Branch] = {}
        self.graph: Graph = []

        self.registry[self.special.any] = (g_always, self.graph)
        self.__modules: set[Callable[[Self], None]] = set()

    def register[B: Branch](self, at: Ty, branch: B) -> Registration[B]:
        if at in self.registry:
            raise KeyError(f"Type `{at}` already taken")
        self.registry[at] = branch
        return self.Registration(self, at, branch)

    def inject[T](self, within: Ty, *node: Node[T]) -> inject[T]:
        return inject.into_branch(self.registry[within], *node)

    def branch(self, at: Ty) -> Branch:
        return self.registry[at]

    def __getitem__(self, at: Ty) -> Branch:
        return self.branch(at)

    def resolve(self, value: Any) -> Query:
        return Query(self.graph, value)

    @staticmethod
    def show(query: Query):
        return query._show()

    def module(self, *inits: Callable[[Self], None]) -> None:
        for init in inits:
            if init not in self.__modules:
                self.__modules.add(init)
                init(self)


# --- Common Nodes ----------------------------------------------------------- #


def g_always[T](obj: T) -> T:
    return obj


def g_instance[T](type_: type[T]) -> Gate[Any, T]:
    def _g_instance(value: Any) -> T:
        if isinstance(value, type_):
            return value
        raise ValueError()

    return _g_instance


def p_identity(value: Any) -> Seg:
    return "=", value


def n_into[From, Into](gate: Gate[From, Into], node: Branch[Into, Any]) -> Branch[From, Into]:
    return (gate, [node])
