import functools
from collections.abc import Callable

__all__ = ["memoize"]


def memoize[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def memoize_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func.__memoize__  # type: ignore
        except AttributeError:
            res = func.__memoize__ = func(*args, **kwargs)  # type: ignore
            return res

    return memoize_wrapper
