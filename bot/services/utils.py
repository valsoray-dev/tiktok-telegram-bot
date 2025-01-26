import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def catch_key_error(func: Callable[P, R]) -> Callable[P, R | None]:
    """Wrap functions that use many dictionary indexing."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        try:
            return func(*args, **kwargs)
        except KeyError as err:
            logging.exception('Key "%s" not found.', err.args[0])
            return None

    return wrapper
