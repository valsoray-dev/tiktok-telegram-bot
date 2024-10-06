from dataclasses import dataclass


@dataclass
class Data:
    video_url: str | None
    music_url: str | None
    images: list[str] | None


@dataclass
class ApiResponse:
    success: bool
    message: str = ""
    data: Data | None = None
