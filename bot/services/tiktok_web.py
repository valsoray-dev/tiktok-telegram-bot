from typing import Any

import orjson
from aiohttp import ClientSession

from ..utils import catch_key_error
from .models import ApiResponse, Data

URL = "https://www.tiktok.com/@i/video/"

errors: dict[str, str] = {
    "item doesn't exist": "video_deleted",
}


async def get_data(aweme_id: int) -> ApiResponse:
    async with ClientSession() as session:
        async with session.get(URL + str(aweme_id)) as response:
            body = await response.text()
            json_str = body.split(
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
            )[1].split("</script>")[0]
            json: dict[str, Any] = orjson.loads(json_str)

            video_detail: dict[str, Any] = json["__DEFAULT_SCOPE__"]["webapp.video-detail"]
            if video_detail.get("statusCode") != 0:
                message: str = video_detail["statusMsg"]
                return ApiResponse(success=False, message=errors.get(message, message))

            data_json: dict[str, Any] = video_detail["itemInfo"]["itemStruct"]
            cookies = "; ".join(f"{key}={value.value}" for key, value in response.cookies.items())

            data = Data(
                video_url=extract_video_url(data_json),
                music_url=extract_music_url(data_json),
                images=extract_images(data_json),
                headers={"cookie": cookies},
            )

            return ApiResponse(success=True, data=data)


@catch_key_error
def extract_video_url(data: dict[str, Any]) -> str | None:
    if "bitrateInfo" not in data["video"]:
        return None

    # it seems like if the first video is not a h265 video,
    # than the first video in bitrateInfo is h264 video from data["video"]["playAddr"]
    return data["video"]["bitrateInfo"][0]["PlayAddr"]["UrlList"][0]


@catch_key_error
def extract_music_url(data: dict[str, Any]) -> str | None:
    if "music" not in data:
        return None

    return data["music"]["playUrl"]


@catch_key_error
def extract_images(data: dict[str, Any]) -> list[str] | None:
    if "imagePost" not in data:
        return None

    images: list[str] = [item["imageURL"]["urlList"][0] for item in data["imagePost"]["images"]]

    return images
