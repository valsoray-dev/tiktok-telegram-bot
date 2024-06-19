from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InputMediaPhoto, Message, URLInputFile
from aiogram.utils.markdown import hlink


def split_list(arr: list[Any], chunk_size: int):
    """
    Splits the list into chunks
    """
    for i in range(0, len(arr), chunk_size):
        yield arr[i : i + chunk_size]


async def handle_video(message: Message, video_url: str):
    await message.bot.send_chat_action(message.chat.id, "upload_video")

    try:
        await message.reply_video(video_url)
    except TelegramBadRequest:
        # video file is bigger than 20 MB
        await message.reply(
            "Це відео завелике тому Телеграм не може його завантажити. "
            f"Ось пряме посилання на це відео: {hlink('CLICK ME', video_url)}"
        )


async def handle_images(message: Message, images: list[str]):
    chunks = split_list(images, 10)

    for chunk in chunks:
        await message.bot.send_chat_action(message.chat.id, "upload_photo")
        media_group = [InputMediaPhoto(media=URLInputFile(image)) for image in chunk]
        await message.reply_media_group(media_group)


async def handle_music(message: Message, music_url: str):
    if not music_url:
        return await message.reply("Музика недоступна")

    await message.bot.send_chat_action(message.chat.id, "upload_audio")

    await message.reply_audio(music_url)
