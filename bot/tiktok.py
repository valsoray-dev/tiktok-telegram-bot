import re

from aiohttp import ClientSession

REQUEST_PARAMS = {
    "version_code": 260103,
    "device_type": "Pixel 7",
    "device_platform": "android",
    "os_version": 13,
    "app_name": "trill",
    "channel": "googleplay",
    "aid": 1180,
}


def get_aweme_id(url: str) -> int | None:
    if aweme_id := re.findall(r"(video|photo)/(\d{19})", url):
        return int(aweme_id[0][1])
    return None


async def get_data(aweme_id: int):
    async with ClientSession() as session:
        async with session.get(
            "https://api22-normal-c-useast2a.tiktokv.com/aweme/v1/feed/",
            params={"aweme_id": aweme_id, **REQUEST_PARAMS},
        ) as response:
            json = await response.json()
            return json["aweme_list"][0]


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
