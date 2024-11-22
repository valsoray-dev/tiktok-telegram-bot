import logging
import re
from typing import Any, Callable, Generator, TypeVar

from aiohttp import ClientSession

T = TypeVar("T")


def split_list(arr: list[Any], chunk_size: int) -> Generator[list[Any], Any, None]:
    """
    Splits the list into chunks
    """
    for i in range(0, len(arr), chunk_size):
        yield arr[i : i + chunk_size]


def get_aweme_id(url: str) -> int | None:
    if match := re.search(r"(?:video|photo|v)/(\d{19})", url):
        return int(match.group(1))
    return None


async def find_tiktok_url(text: str) -> str | None:
    match: re.Match[str] | None = re.search(r"(?:www|vm)\.tiktok\.com/[^\s]+", text)
    if not match:
        return None

    url: str = "https://" + match.group()
    match url.split("/")[2]:
        # TikTok Web
        case "www.tiktok.com":
            return url

        # Mobile App
        case "vm.tiktok.com":
            async with ClientSession() as session:
                async with session.options(url, allow_redirects=False) as request:
                    return request.headers["Location"]
        case _:
            return None


def catch_key_error(func: Callable[..., T]) -> Callable[..., T | None]:
    """
    Wrapper for functions that use many dictionary indexing
    """

    def wrapper(*args: Any, **kwargs: Any) -> T | None:
        try:
            return func(*args, **kwargs)
        except KeyError as err:
            logging.error(f'({func.__name__}) Key "{err.args[0]}" not found.')
            return None

    return wrapper
