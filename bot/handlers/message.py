import logging
from os import getenv

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
    URLInputFile,
)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.media_group import MediaGroupBuilder

from ..services import tiktok
from ..services.models import ApiResponse
from ..utils import find_tiktok_url, get_aweme_id, split_list

message_router = Router()


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

    response: ApiResponse = await tiktok.get_data(aweme_id)
    if not response.success:
        match response.message:
            case "Video has been removed":
                return await message.reply("Це відео було видалено з ТікТоку.")
            case "Server is currently unavailable. Please try again later.":
                return await message.reply(
                    "У цей момент сервера ТікТоку не доступні. "
                    "Спробуйте ще раз через декілька секунд."
                )
            case _:
                return await handle_unexpected_tiktok_api_error(
                    bot, message, url, response.message
                )

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
                    video_url,
                    reply_markup=assemble_inline_keyboard(aweme_id, music_url),
                )
        except TelegramBadRequest as e:
            match e.message:
                # video file is bigger than 20 MB
                # or something else, i don't know
                case "Bad Request: failed to get HTTP URL content":
                    await message.reply(
                        "Це відео завелике (або щось пішло не так) "
                        "тому Телеграм не може його завантажити. "
                        f"Ось пряме посилання на це відео: {html.link('CLICK ME', video_url)}"
                    )
                case _:
                    raise e


def assemble_inline_keyboard(
    aweme_id: int, music_url: str | None
) -> InlineKeyboardMarkup:
    """Create an inline keyboard with Music and HD buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Music", url=music_url),
                InlineKeyboardButton(
                    text="HD",
                    url=f"https://www.tikwm.com/video/media/hdplay/{aweme_id}.mp4",
                ),
            ]
        ]
    )


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
        "ТікТок повернув несподівану помилку. "
        "Інформація про цю помилку була направлена розробнику."
    )
