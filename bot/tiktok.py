import re

from aiohttp import ClientSession


def get_aweme_id(url: str) -> int | None:
    if aweme_id := re.findall(r"(video|photo)/(\d{19})", url):
        return int(aweme_id[0][1])
    return None


async def get_data(aweme_id: int):
    async with ClientSession() as session:
        async with session.get(
            "https://tikwm.com/api", params={"url": aweme_id, "hd": 1}
        ) as response:
            json = await response.json()
            if json["code"] != 0:
                raise Exception(json["msg"])
            return json["data"]


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
            return
