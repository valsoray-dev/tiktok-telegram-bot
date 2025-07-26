from abc import ABC, abstractmethod

from pydantic import BaseModel

from bot.utils import HeaderMap


class Data(BaseModel):
    video_url: str | None
    music_url: str | None
    images: list[str] | None
    is_age_restricted: bool = False
    headers: HeaderMap | None = None


class ApiResponse(BaseModel):
    success: bool
    message: str | None = None
    data: Data | None = None


class BaseParser(ABC):
    @abstractmethod
    async def parse(self, aweme_id: int) -> ApiResponse:
        pass
