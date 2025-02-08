import logging
import re
from os import getenv

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    URLInputFile,
)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiohttp import ClientSession

from ..services import tiktok_web
from ..services.models import ApiResponse
from ..utils import split_list

message_router = Router()

TIKTOK_URL_REGEX = r"((?:www|vm|vt)\.tiktok\.com)/[^\s]+"
TIKWM_HD_URL = "https://www.tikwm.com/video/media/hdplay/{}.mp4"


@message_router.message(F.text)
async def url_handler(message: Message, bot: Bot):
    assert message.text is not None

    url = await find_tiktok_url(message.text)

    # if url not found in user message, just ignore it
    if not url:
        return None

    aweme_id = get_aweme_id(url)

    if not aweme_id:
        logging.warning("Failed to get Aweme ID.\nURL: [%s]", url)
        return await message.reply(
            "За вашим посиланням нічого не знайдено. "
            "Перевірте його правильність та спробуйте ще раз."
        )

    response: ApiResponse = await tiktok_web.get_data(aweme_id)
    if not response.success:
        match response.message:
            case "video_deleted":
                return await message.reply("Це відео було видалено з ТікТоку.")
            case "service_unavailable":
                return await message.reply(
                    "У цей момент сервера ТікТоку не доступні. "
                    "Спробуйте ще раз через декілька секунд."
                )
            case _:
                return await handle_unexpected_tiktok_api_error(bot, message, url, response.message)

    assert response.data is not None

    if response.data.images:
        chunks = split_list(response.data.images, 10)
        for chunk in chunks:
            async with ChatActionSender.upload_photo(
                message.chat.id, bot, message.message_thread_id
            ):
                media_group = MediaGroupBuilder(
                    [InputMediaPhoto(media=URLInputFile(image)) for image in chunk]
                )
                await message.reply_media_group(media_group.build())

    elif response.data.video_url:
        video_url = response.data.video_url
        music_url = response.data.music_url

        try:
            async with ChatActionSender.upload_video(
                message.chat.id, bot, message.message_thread_id
            ):
                await message.reply_video(
                    URLInputFile(video_url, headers=response.data.headers),
                    reply_markup=assemble_inline_keyboard(aweme_id, music_url),
                )
        except TelegramBadRequest as e:
            match e.message:
                # video file is bigger than 20 MB
                # or something else, i don't know
                case "Bad Request: failed to get HTTP URL content":
                    await message.reply(
                        "Це відео завелике (або щось пішло не так) "
                        "тому Телеграм не може його завантажити.<br>"
                        f"Ось пряме посилання на це відео: {html.link('CLICK ME', video_url)}<br>"
                        f"Або ось пряме посилання на HD версію: {html.link('CLICK ME', TIKWM_HD_URL.format(aweme_id))}",
                    )
                case _:
                    raise e


def get_aweme_id(url: str) -> int | None:
    if match := re.search(r"(?:video|photo|v)/(\d{19})", url):
        return int(match.group(1))
    return None


async def find_tiktok_url(text: str) -> str | None:
    match: re.Match[str] | None = re.search(TIKTOK_URL_REGEX, text)
    if not match:
        return None

    url: str = "https://" + match.group()
    domain: str = match.group(1)
    match domain:
        # TikTok Web
        case "www.tiktok.com":
            return url

        # Mobile App
        case "vm.tiktok.com" | "vt.tiktok.com":
            async with ClientSession() as session:
                async with session.options(url, allow_redirects=False) as request:
                    return request.headers["Location"]
        case _:
            return None


def assemble_inline_keyboard(aweme_id: int, music_url: str | None) -> InlineKeyboardMarkup:
    """Create an inline keyboard with Music and HD buttons."""
    builder = InlineKeyboardBuilder()

    if music_url:
        builder.button(text="Music", url=music_url)

    builder.button(text="HD", url=TIKWM_HD_URL.format(aweme_id))

    return builder.as_markup()


async def handle_unexpected_tiktok_api_error(
    bot: Bot, message: Message, url: str, api_message: str | None
) -> None:
    from dotenv import load_dotenv

    load_dotenv()

    error_text = f"Unexpected error from API: {api_message}\nURL: [{url}]"

    logging.error(error_text)
    if owner_id := getenv("OWNER_ID"):
        await bot.send_message(owner_id, error_text)

    await message.reply(
        "ТікТок повернув несподівану помилку. Інформація про цю помилку була направлена розробнику."
    )
