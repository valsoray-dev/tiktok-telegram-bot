# ruff: noqa: E501

import logging

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest, TelegramEntityTooLarge
from aiogram.types import (
    InputMediaPhoto,
    Message,
    URLInputFile,
)
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.media_group import MediaGroupBuilder
from aiohttp import ClientSession

from bot.config import AWEME_ID_PATTERN, OWNER_ID, TIKTOK_URL_PATTERN, TIKWM_HD_URL, TIKWM_PLAY_URL
from bot.services import ApiResponse, Data, tiktok_web
from bot.utils import HeaderMap, split_list_into_chunks

logger = logging.getLogger(__name__)


message_router = Router()


@message_router.message(F.text)
async def url_handler(message: Message, bot: Bot) -> None:
    assert message.text is not None

    url = await resolve_tiktok_url(message.text)
    if not url:
        return None  # if url not found in user message, just ignore it

    aweme_id = extract_aweme_id(url)
    if not aweme_id:
        logger.warning("Failed to get Aweme ID.\nURL: [%s]", url)
        await message.reply(
            "За вашим посиланням нічого не знайдено. "
            "Перевірте його правильність та спробуйте ще раз.",
        )
        return None

    response: ApiResponse = await tiktok_web.TikTokWebParser().parse(aweme_id)
    if not response.success:
        if response.message == "geo_restricted":
            response.success = True
            response.data = Data(
                video_url=TIKWM_PLAY_URL.format(aweme_id),
                music_url=None,
                images=None,
            )
        else:
            return await handle_tiktok_error(bot, message, url, response.message)

    assert response.data is not None

    if response.data.is_age_restricted:
        # return await message.reply("Це відео обмежено за віком.")
        response.data.video_url = TIKWM_PLAY_URL.format(aweme_id)

    if response.data.images:
        await handle_image_post(
            bot,
            message,
            response.data.images,
            response.data.headers,
        )

    elif response.data.video_url:
        await handle_video_post(
            bot,
            message,
            response.data.headers,
            response.data.video_url,
            aweme_id,
        )

    return None


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
            async with (
                ClientSession() as session,
                session.options(url, allow_redirects=False) as request,
            ):
                return request.headers["Location"]
        case _:
            return None


async def handle_image_post(
    bot: Bot,
    message: Message,
    images: list[str],
    headers: HeaderMap | None,
) -> None:
    if headers is not None:
        # don't ask why
        headers.pop("Cookie", None)

    chunks = split_list_into_chunks(images, 10)
    for chunk in chunks:
        async with ChatActionSender.upload_photo(message.chat.id, bot, message.message_thread_id):
            media_group = MediaGroupBuilder(
                [
                    InputMediaPhoto(media=URLInputFile(image, headers.data if headers else None))
                    for image in chunk
                ],
            )
            await message.reply_media_group(media_group.build())


async def handle_video_post(
    bot: Bot,
    message: Message,
    headers: HeaderMap | None,
    video_url: str,
    aweme_id: int,
) -> None:
    try:
        async with ChatActionSender.upload_video(message.chat.id, bot, message.message_thread_id):
            await message.reply_video(URLInputFile(video_url, headers.data if headers else None))
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
                    "Це відео завелике (або щось пішло не так) тому Телеграм не може його завантажити.\n"
                    f"Ось пряме посилання на це відео: {html.link('CLICK ME', TIKWM_PLAY_URL.format(aweme_id))}\n"
                    f"Або ось пряме посилання на HD версію: {html.link('CLICK ME', TIKWM_HD_URL.format(aweme_id))}",
                )
            case _:
                raise


async def handle_tiktok_error(
    bot: Bot,
    message: Message,
    url: str,
    api_message: str | None,
) -> None:
    """Handle errors from TikTok API."""
    match api_message:
        case (
            "video_unavailable"
            | "status_deleted"
            | "status_self_see"
            | "status_reviewing"
            | "status_audit_not_pass"
        ):
            await message.reply("Це відео недоступне для завантаження.")
        case "account_private":
            await message.reply("Це відео належить приватному аккаунту.")
        case "item_is_storypost":
            await message.reply(
                "Це відео є сторійпостом. Я не можу його завантажити. "
                "Спробуйте завантажити тут: https://www.tikwm.com/",
            )
        case "server_unavailable":
            await message.reply(
                "У цей момент сервера ТікТоку не доступні. Спробуйте ще раз через декілька секунд.",
            )
        case _:
            return await handle_unexpected_tiktok_error(bot, message, url, api_message)

    return None


async def handle_unexpected_tiktok_error(
    bot: Bot,
    message: Message,
    url: str,
    api_message: str | None,
) -> None:
    """Handle unexpected errors from TikTok API."""
    error_text = f"Unexpected error from API: `{api_message}`\nURL: [{url}]"
    logger.error(error_text)

    if OWNER_ID:
        await bot.send_message(OWNER_ID, error_text)

    await message.reply(
        "Я не можу завантажити це відео з ТікТоку. "
        "Скоріше за все, воно не доступне для завантаження. "
        "Спробуйте ще раз трошки пізніше.",
    )
