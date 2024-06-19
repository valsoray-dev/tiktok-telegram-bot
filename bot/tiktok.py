import re

from aiohttp import ClientSession

URL = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/multi/aweme/detail/"

PARAMS = {
    # The first two appear after installing the application
    "iid": 7379691220551141126,
    "device_id": 7379690547022071302,
    "channel": "googleplay",
    "aid": 1233,
    "app_name": "musical_ly",
    "version_code": 350103,
    "version_name": "35.1.3",
    "device_platform": "android",
    "device_type": "Pixel 8 Pro",
    "os_version": 14,
}

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "com.zhiliaoapp.musically/2023501030 (Linux; U; Android 14; en_US; Pixel 8 Pro; Build/TP1A.220624.014;tt-ok/3.12.13.4-tiktok)",
    "X-Argus": "",  # It just has to be there. There are no checks on the server
}


def get_aweme_id(url: str) -> int | None:
    if aweme_id := re.findall(r"(video|photo)/(\d{19})", url):
        return int(aweme_id[0][1])
    return None


async def get_data(aweme_id: int):
    async with ClientSession() as session:
        async with session.post(
            URL, data={"aweme_ids": f"[{aweme_id}]"}, params=PARAMS, headers=HEADERS
        ) as response:
            json = await response.json()
            if json["status_code"] != 0:
                raise Exception(json["statu_msg"])
            return json["aweme_details"][0]


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
