import logging

from aiohttp import ClientSession
from typing_extensions import override

from bot.config import DEVICE_ID, INSTALL_ID
from bot.services import ApiResponse, BaseParser, Data
from bot.services.tiktok_api.models import AwemeDetail, Root
from bot.utils import HeaderMap

logger = logging.getLogger(__name__)


if not INSTALL_ID or not DEVICE_ID:
    msg = "INSTALL_ID and DEVICE_ID should be in .env"
    raise ValueError(msg)

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

HEADERS = HeaderMap(
    {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "com.zhiliaoapp.musically/2023501030 (Linux; U; Android 14; en_US; Pixel 8 Pro; Build/TP1A.220624.014;tt-ok/3.12.13.4-tiktok)",  # noqa: E501
        "X-Argus": "",  # It just has to be there. There are no checks on the server
    },
)

ERRORS: dict[str, str] = {
    "Video has been removed": "video_unavailable",
    "Server is currently unavailable. Please try again later.": "server_unavailable",
}


class TikTokAPIParser(BaseParser):
    @override
    async def parse(self, aweme_id: int) -> ApiResponse:
        async with (
            ClientSession() as session,
            session.post(
                URL,
                data={"aweme_ids": f"[{aweme_id}]"},
                params=PARAMS,
                headers=HEADERS,
            ) as response,
        ):
            # it happens from time to time
            if response.status == 504:  # noqa: PLR2004
                logger.warning("[TikTok API] API responded with HTTP status 504, trying again.")
                return await self.parse(aweme_id)

            text = await response.text()
            if not text:
                # Note: if INSTALL_ID and/or DEVICE_ID are incorrect, here will be infinity loop
                # TODO: add something like limits on recursion
                logger.warning("[TikTok API] Response body is empty, trying again.")
                return await self.parse(aweme_id)

            model = Root.model_validate_json(text)
            if model.status_code != 0:
                message: str = model.status_msg
                return ApiResponse(success=False, message=ERRORS.get(message, message))

            aweme_detail = model.aweme_details[0]
            data = Data(
                video_url=extract_video_url(aweme_detail),
                music_url=extract_music_url(aweme_detail),
                images=extract_images(aweme_detail),
            )

            return ApiResponse(success=True, data=data)


def extract_video_url(data: AwemeDetail) -> str | None:
    video_url: str | None = None

    # find the video with h265 codec (better quality, less size)
    for item in data.video.bit_rate:
        # if the video is not encoded with proprietary bvc2 codec
        if (
            item.is_bytevc1 is not None
            and item.is_bytevc1 != 2  # noqa: PLR2004
            and len(item.play_addr.url_list) != 0
        ):
            video_url = item.play_addr.url_list[0]
            break

    # if not found the video with h265 codec
    # it's not likely to happen, but just in case
    if not video_url:
        video_url = data.video.play_addr.url_list[0]

    return video_url


def extract_music_url(data: AwemeDetail) -> str | None:
    if data.music is None:
        return None

    return data.music.play_url.uri


def extract_images(data: AwemeDetail) -> list[str] | None:
    if data.image_post_info is None:
        return None

    return [
        item.display_image.url_list[
            -1  # there are two elements: first is .heic, second is .jpeg
        ]
        for item in data.image_post_info.images
    ]
