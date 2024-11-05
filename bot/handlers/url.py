import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto, Message, URLInputFile
from aiogram.utils.markdown import hlink

from bot.services import tiktok
from bot.services.models import ApiResponse
from bot.utils import find_tiktok_url, get_aweme_id, split_list

url_router = Router()


@url_router.message(F.text)
async def url_handler(message: Message):
    url = await find_tiktok_url(message.text)  # type: ignore

    if not url:
        logging.warning(
            f"Couldn't find the TikTok link in message text.\nTEXT: [{message.text}]"
        )
        return await message.reply("Я не знайшов посилання на ТікТок в Вашому тексті!")

    aweme_id = get_aweme_id(url)

    if not aweme_id:
        logging.warning(f"Failed to get Aweme ID.\nURL: [{url}]")
        return await message.reply(
            "При обробці вашого посилання сталася помилка. Перевірте посилання та спробуйте ще раз!"
        )

    response: ApiResponse = await tiktok.get_data(aweme_id)
    if not response.success:
        match response.message:
            case "Video has been removed":
                return await message.reply("Це відео було видалено з ТікТоку!")
            case _:
                raise Exception(
                    f"Unexpected error from API: {response.message}\nURL: [{url}]"
                )

    if not response.data.images:
        video_url = response.data.video_url
        await message.bot.send_chat_action(message.chat.id, "upload_video")

        try:
            await message.reply_video(video_url)
        except TelegramBadRequest as e:
            match e.message:
                # video file is bigger than 20 MB
                # or something else, i don't know
                case "Bad Request: failed to get HTTP URL content":
                    await message.reply(
                        "Це відео завелике тому Телеграм не може його завантажити. "
                        f"Ось пряме посилання на це відео: {hlink('CLICK ME', video_url)}"
                    )
                case _:
                    raise e
    else:
        chunks = split_list(response.data.images, 10)
        for chunk in chunks:
            await message.bot.send_chat_action(message.chat.id, "upload_photo")
            media_group = [
                InputMediaPhoto(media=URLInputFile(image)) for image in chunk
            ]
            await message.reply_media_group(media_group)

    # music_url = response.data.music_url
    # if not music_url:
    #     return await message.reply("Музика недоступна")

    # await message.bot.send_chat_action(message.chat.id, "upload_audio")
    # await message.reply_audio(music_url)
