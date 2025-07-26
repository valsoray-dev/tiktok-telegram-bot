from pydantic import BaseModel


class PlayAddr(BaseModel):
    url_list: list[str]


class BitRate(BaseModel):
    play_addr: PlayAddr
    is_bytevc1: int | None = None


class Video(BaseModel):
    bit_rate: list[BitRate]
    play_addr: PlayAddr


class PlayUrl(BaseModel):
    uri: str


class Music(BaseModel):
    play_url: PlayUrl


class DisplayImage(BaseModel):
    url_list: list[str]


class ImageItem(BaseModel):
    display_image: DisplayImage


class ImagePostInfo(BaseModel):
    images: list[ImageItem]


class AwemeDetail(BaseModel):
    video: Video
    music: Music | None = None
    image_post_info: ImagePostInfo | None = None


class Root(BaseModel):
    status_code: int
    status_msg: str
    aweme_details: list[AwemeDetail]
