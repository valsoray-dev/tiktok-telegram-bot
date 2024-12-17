import re
from typing import Any, Generator

from aiohttp import ClientSession


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
    match: re.Match[str] | None = re.search(
        r"((?:www|vm|vt)\.tiktok\.com)/[^\s]+", text
    )
    if not match:
        return None

    url: str = "https://" + match.group()
    domain: str = match.group(1)
    match domain:
        # TikTok Web
        case "www.tiktok.com":
            return url

        # Mobile App
        case "vm.tiktok.com" | "vt.tiktok.com":
            async with ClientSession() as session:
                async with session.options(url, allow_redirects=False) as request:
                    return request.headers["Location"]
        case _:
            return None
