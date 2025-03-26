import logging

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge
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

from ..config import AWEME_ID_PATTERN, OWNER_ID, TIKTOK_URL_PATTERN, TIKWM_HD_URL, TIKWM_PLAY_URL
from ..services import tiktok_api, tiktok_web
from ..services.models import ApiResponse, Data
from ..utils import split_list

message_router = Router()


@message_router.message(F.text)
async def url_handler(message: Message, bot: Bot):
    assert message.text is not None

    url = await resolve_tiktok_url(message.text)
    if not url:
        return None  # if url not found in user message, just ignore it

    aweme_id = extract_aweme_id(url)
    if not aweme_id:
        logging.warning("Failed to get Aweme ID.\nURL: [%s]", url)
        return await message.reply(
            "За вашим посиланням нічого не знайдено. "
            "Перевірте його правильність та спробуйте ще раз."
        )

    response: ApiResponse = await tiktok_web.get_data(aweme_id)
    if not response.success:
        return await handle_tiktok_error(bot, message, url, response.message)

    assert response.data is not None

    if response.data.is_age_restricted:
        response: ApiResponse = await tiktok_api.get_data(aweme_id)
        if not response.success:
            return await handle_tiktok_error(bot, message, url, response.message)
        assert response.data is not None

    if response.data.images:
        await handle_image_post(bot, message, response.data)

    elif response.data.video_url:
        await handle_video_post(bot, message, response.data, aweme_id)


def extract_aweme_id(url: str) -> int | None:
    if match := AWEME_ID_PATTERN.search(url):
        return int(match.group(1))
    return None


async def resolve_tiktok_url(text: str) -> str | None:
    match = TIKTOK_URL_PATTERN.search(text)
    if not match:
        return None

    url = "https://" + match.group()
    domain = match.group(1)
    match domain:
        # TikTok Web
        case "www.tiktok.com":
            return url

        # Mobile App
        case "vm.tiktok.com" | "vt.tiktok.com":
            async with ClientSession() as session:
                async with session.options(url, allow_redirects=False) as request:
                    return request.headers["Location"]
    return None


async def handle_image_post(bot: Bot, message: Message, data: Data) -> None:
    assert data.images is not None

    chunks = split_list(data.images, 10)
    for chunk in chunks:
        async with ChatActionSender.upload_photo(message.chat.id, bot, message.message_thread_id):
            media_group = MediaGroupBuilder(
                [InputMediaPhoto(media=URLInputFile(image)) for image in chunk]
            )
            await message.reply_media_group(media_group.build())


async def handle_video_post(bot: Bot, message: Message, data: Data, aweme_id: int) -> None:
    assert data.video_url is not None
    assert data.music_url is not None

    video_url = data.video_url
    music_url = data.music_url
    is_private = message.chat.type == "private"

    try:
        async with ChatActionSender.upload_video(message.chat.id, bot, message.message_thread_id):
            await message.reply_video(
                URLInputFile(video_url, headers=data.headers),
                reply_markup=assemble_inline_keyboard(aweme_id, music_url) if is_private else None,
            )
    except TelegramEntityTooLarge:
        await message.reply(
            "Це відео завелике тому Телеграм не може його завантажити.\n"
            f"Ось пряме посилання на це відео: {html.link('CLICK ME', TIKWM_PLAY_URL.format(aweme_id))}\n"
            f"Або ось пряме посилання на HD версію: {html.link('CLICK ME', TIKWM_HD_URL.format(aweme_id))}",
        )
    except TelegramBadRequest as exception:
        match exception.message:
            # video file is bigger than 20 MB
            # or something else, i don't know
            case "Bad Request: failed to get HTTP URL content":
                await message.reply(
                    "Це відео завелике (або щось пішло не так) "
                    "тому Телеграм не може його завантажити.\n"
                    f"Ось пряме посилання на це відео: {html.link('CLICK ME', TIKWM_PLAY_URL.format(aweme_id))}\n"
                    f"Або ось пряме посилання на HD версію: {html.link('CLICK ME', TIKWM_HD_URL.format(aweme_id))}",
                )
            case _:
                raise exception


def assemble_inline_keyboard(aweme_id: int, music_url: str | None) -> InlineKeyboardMarkup:
    """Create an inline keyboard with Music and HD buttons."""
    builder = InlineKeyboardBuilder()

    if music_url:
        builder.button(text="Music", url=music_url)

    builder.button(text="HD", url=TIKWM_HD_URL.format(aweme_id))

    return builder.as_markup()


async def handle_tiktok_error(
    bot: Bot, message: Message, url: str, api_message: str | None
) -> None:
    """Handle errors from TikTok API."""
    match api_message:
        case "video_unavailable":
            await message.reply("Я не можу отримати інформацію про це відео.")
        case "account_private":
            await message.reply("Це відео належить приватному аккаунту.")
        case "item_is_storypost":
            await message.reply(
                "Це відео є сторійпостом. Я не можу його завантажити. Спробуйте це: https://www.tikwm.com/"
            )
        case "server_unavailable":
            await message.reply(
                "У цей момент сервера ТікТоку не доступні. Спробуйте ще раз через декілька секунд."
            )
        case _:
            return await handle_unexpected_tiktok_error(bot, message, url, api_message)


async def handle_unexpected_tiktok_error(
    bot: Bot, message: Message, url: str, api_message: str | None
) -> None:
    """Handle unexpected errors from TikTok API."""
    error_text = f"Unexpected error from API: `{api_message}`\nURL: [{url}]"
    logging.error(error_text)

    if OWNER_ID:
        await bot.send_message(OWNER_ID, error_text)

    await message.reply(
        "Я не можу завантажити це з ТікТоку. Скоріше за все, це не доступне для завантаження. "
        "Спробуйте ще раз через пізніше."
    )
