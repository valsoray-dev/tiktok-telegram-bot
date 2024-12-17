from typing import Any

import orjson
from aiohttp import ClientSession

from .models import ApiResponse, Data

URL = "https://www.tikwm.com/api/"


async def get_data(aweme_id: int) -> ApiResponse:
    async with ClientSession() as session:
        async with session.post(URL, data={"url": aweme_id, "hd": 1}) as response:
            json: dict[str, Any] = await response.json(loads=orjson.loads)
            if json["code"] != 0:
                return ApiResponse(success=False, message=json["msg"])

            data_json: dict[str, Any] = json["data"]
            data = Data(
                video_url=data_json.get("hdplay"),
                music_url=data_json.get("music"),
                images=data_json.get("images"),
            )

            return ApiResponse(success=True, data=data)
