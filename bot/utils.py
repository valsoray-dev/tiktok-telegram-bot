import re
from typing import Any

from aiohttp import ClientSession


def split_list(arr: list[Any], chunk_size: int):
    """
    Splits the list into chunks
    """
    for i in range(0, len(arr), chunk_size):
        yield arr[i : i + chunk_size]


def get_aweme_id(url: str) -> int | None:
    if aweme_id := re.findall(r"(video|photo)/(\d{19})", url):
        return int(aweme_id[0][1])
    return None


async def get_redirect_url(url: str) -> str | None:
    match url.removeprefix("https://").split("/")[0]:
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
