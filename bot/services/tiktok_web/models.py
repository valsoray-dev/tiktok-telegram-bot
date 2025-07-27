# ruff: noqa: N815

from pydantic import BaseModel, Field


class PlayAddr(BaseModel):
    UrlList: list[str]


class BitrateInfo(BaseModel):
    PlayAddr: PlayAddr


class Video(BaseModel):
    playAddr: str | None = None  # leave it here just in case
    bitrateInfo: list[BitrateInfo] | None = None


class Music(BaseModel):
    playUrl: str


class ImageURL(BaseModel):
    urlList: list[str]


class Image(BaseModel):
    imageURL: ImageURL


class ImagePost(BaseModel):
    images: list[Image]


class ItemStruct(BaseModel):
    video: Video
    music: Music | None = None
    imagePost: ImagePost | None = None
    isContentClassified: bool = False


class ItemInfo(BaseModel):
    itemStruct: ItemStruct


class WebappVideoDetail(BaseModel):
    itemInfo: ItemInfo
    statusCode: int
    statusMsg: str


class DefaultScope(BaseModel):
    webapp_video_detail: WebappVideoDetail = Field(alias="webapp.video-detail")


class Root(BaseModel):
    default_scope: DefaultScope = Field(alias="__DEFAULT_SCOPE__")
