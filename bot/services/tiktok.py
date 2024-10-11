import logging
from os import getenv
from typing import Any

import orjson
from aiohttp import ClientSession
from dotenv import load_dotenv

from bot.services.models import ApiResponse, Data

load_dotenv()
INSTALL_ID: str | None = getenv("INSTALL_ID")
DEVICE_ID: str | None = getenv("DEVICE_ID")

if not INSTALL_ID or not DEVICE_ID:
    raise ValueError("INSTALL_ID and DEVICE_ID should be in .env")

URL = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/multi/aweme/detail/"

PARAMS: dict[str, str] = {
    # The first two appear after installing the application
    "iid": INSTALL_ID,
    "device_id": DEVICE_ID,
    "channel": "googleplay",
    "aid": "1233",
    "app_name": "musical_ly",
    "version_code": "350103",
    "version_name": "35.1.3",
    "device_platform": "android",
    "device_type": "Pixel 8 Pro",
    "os_version": "14",
}

HEADERS: dict[str, str] = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "com.zhiliaoapp.musically/2023501030 (Linux; U; Android 14; en_US; Pixel 8 Pro; Build/TP1A.220624.014;tt-ok/3.12.13.4-tiktok)",
    "X-Argus": "",  # It just has to be there. There are no checks on the server
}


async def get_data(aweme_id: int) -> ApiResponse:
    async with ClientSession() as session:
        async with session.post(
            URL, data={"aweme_ids": f"[{aweme_id}]"}, params=PARAMS, headers=HEADERS
        ) as response:
            json: dict[str, Any] = await response.json(loads=orjson.loads)
            if json is None:
                logging.warning("JSON Response is empty, trying again.")
                return await get_data(aweme_id)

            if json.get("status_code") != 0:
                return ApiResponse(success=False, message=json.get("status_msg"))

            # can only access if `status_code` present and it's not None
            # so it's safe (i think so)
            data_json: dict[str, Any] = json["aweme_details"][0]
            data = Data(
                video_url=extract_video_url(data_json),
                music_url=extract_music_url(data_json),
                images=extract_images(data_json),
            )

            return ApiResponse(success=True, data=data)


def extract_video_url(data: dict[str, Any]) -> str | None:
    video_url: str | None = None

    for item in data["video"]["bit_rate"]:
        # if the video is not encoded with proprietary bvc2 codec
        if "is_bytevc1" in item and item["is_bytevc1"] != 2:
            video_url = item["play_addr"]["url_list"][0]
            break

    # if no video was found according to the above criteria
    # it's not likely to happen, but just in case
    if not video_url:
        video_url = data["video"]["play_addr"]["url_list"][0]

    return video_url


def extract_music_url(data: dict[str, Any]) -> str | None:
    music_url: str | None = data["music"]["play_url"]["uri"]

    return music_url


def extract_images(data: dict[str, Any]) -> list[str] | None:
    if "image_post_info" not in data:
        return None

    images: list[str] = [
        item["display_image"]["url_list"][-1]  # first is .heic, second is .jpeg
        for item in data["image_post_info"]["images"]
    ]

    return images
