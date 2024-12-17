import logging
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def catch_key_error(func: Callable[..., T]) -> Callable[..., T | None]:
    """
    Wrapper for functions that use many dictionary indexing
    """

    def wrapper(*args: Any, **kwargs: Any) -> T | None:
        try:
            return func(*args, **kwargs)
        except KeyError as err:
            logging.error('(%s) Key "%s" not found.', func.__name__, err.args[0])
            return None

    return wrapper
