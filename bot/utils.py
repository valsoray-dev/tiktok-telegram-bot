import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")


def catch_key_error(func: Callable[P, R]) -> Callable[P, R]:
    """Wrap functions that use many dictionary indexing."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except KeyError as err:
            logging.error('Key "%s" not found.', err.args[0])
            raise err

    return wrapper


def split_list(arr: list[T], chunk_size: int) -> list[list[T]]:
    """Split the list into chunks."""
    return [arr[i : i + chunk_size] for i in range(0, len(arr), chunk_size)]
