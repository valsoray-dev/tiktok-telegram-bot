import logging

from aiohttp import ClientSession
from typing_extensions import override

from bot.services import ApiResponse, BaseParser, Data
from bot.utils import HeaderMap

from .models import ItemStruct, Root

logger = logging.getLogger(__name__)


URL = "https://www.tiktok.com/@i/video/"

HEADERS = HeaderMap(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",  # noqa: E501
    },
)


ERRORS: dict[str, str] = {
    "item doesn't exist": "video_unavailable",
    "author_secret": "account_private",
    "item is storypost": "item_is_storypost",
    "cross_border_violation": "geo_restricted",
}


class TikTokWebParser(BaseParser):
    @override
    async def parse(self, aweme_id: int) -> ApiResponse:
        async with (
            ClientSession() as session,
            session.get(URL + str(aweme_id), headers=HEADERS) as response,
        ):
            body = await response.text()
            try:
                json_str = body.split(
                    '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">',
                )[1].split("</script>")[0]
            except IndexError:
                # i think it should work
                logger.warning("[TikTok Web] Needed HTML tag not found, trying again.")
                return await self.parse(aweme_id)

            model = Root.model_validate_json(json_str)
            video_detail = model.default_scope.webapp_video_detail
            if video_detail.statusCode != 0:
                message = video_detail.statusMsg
                return ApiResponse(success=False, message=ERRORS.get(message, message))

            item_struct = video_detail.itemInfo.itemStruct
            cookies = "; ".join(f"{key}={value.value}" for key, value in response.cookies.items())

            data = Data(
                video_url=extract_video_url(item_struct),
                music_url=extract_music_url(item_struct),
                images=extract_images(item_struct),
                is_age_restricted=item_struct.isContentClassified,
                headers=HEADERS | {"Cookie": cookies, "Referer": "https://www.tiktok.com/"},
            )

            return ApiResponse(success=True, data=data)


def extract_video_url(data: ItemStruct) -> str | None:
    if data.video.bitrateInfo is None:
        return None

    # Note: If the first entry in bitrateInfo is not an h265 video,
    # it is likely an h264 video, corresponding to `item_struct.video.playAddr`
    return data.video.bitrateInfo[0].PlayAddr.UrlList[0]


def extract_music_url(data: ItemStruct) -> str | None:
    if data.music is None:
        return None

    return data.music.playUrl


def extract_images(data: ItemStruct) -> list[str] | None:
    if data.imagePost is None:
        return None

    images: list[str] = [item.imageURL.urlList[0] for item in data.imagePost.images]

    return images
