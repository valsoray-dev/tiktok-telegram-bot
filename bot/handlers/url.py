import logging

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto, Message, URLInputFile
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.media_group import MediaGroupBuilder

from bot.services import tiktok
from bot.services.models import ApiResponse
from bot.utils import find_tiktok_url, get_aweme_id, split_list

url_router = Router()


@url_router.message(F.text)
async def url_handler(message: Message, bot: Bot):
    assert message.text

    url = await find_tiktok_url(message.text)

    # if url not found in user message, just ignore it
    if not url:
        return

    aweme_id = get_aweme_id(url)

    if not aweme_id:
        logging.warning(f"Failed to get Aweme ID.\nURL: [{url}]")
        return await message.reply(
            "За вашим посиланням нічого не знайдено. Перевірте його правильність та спробуйте ще раз."
        )

    response: ApiResponse = await tiktok.get_data(aweme_id)
    if not response.success:
        match response.message:
            case "Video has been removed":
                return await message.reply("Це відео було видалено з ТікТоку.")
            case _:
                raise Exception(
                    f"Unexpected error from API: {response.message}\nURL: [{url}]"
                )

    assert response.data is not None

    if not response.data.images:
        video_url = response.data.video_url
        assert video_url is not None

        try:
            async with ChatActionSender.upload_video(
                message.chat.id, bot, message.message_thread_id
            ):
                await message.reply_video(video_url)
        except TelegramBadRequest as e:
            match e.message:
                # video file is bigger than 20 MB
                # or something else, i don't know
                case "Bad Request: failed to get HTTP URL content":
                    await message.reply(
                        "Це відео завелике тому Телеграм не може його завантажити. "
                        f"Ось пряме посилання на це відео: {html.link('CLICK ME', video_url)}"
                    )
                case _:
                    raise e
    else:
        chunks = split_list(response.data.images, 10)
        for chunk in chunks:
            async with ChatActionSender.upload_photo(
                message.chat.id, bot, message.message_thread_id
            ):
                media_group = MediaGroupBuilder(
                    [InputMediaPhoto(media=URLInputFile(image)) for image in chunk]
                )
                await message.reply_media_group(media_group.build())
