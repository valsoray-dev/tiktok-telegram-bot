from dataclasses import dataclass
from typing import Any


@dataclass
class Data:
    video_url: str | None
    music_url: str | None
    images: list[str] | None
    is_age_restricted: bool | None = None
    headers: dict[str, Any] | None = None


@dataclass
class ApiResponse:
    success: bool
    message: str | None = None
    data: Data | None = None
