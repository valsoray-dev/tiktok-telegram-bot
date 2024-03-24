import asyncio
import logging

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import ErrorEvent, Message

from bot.tiktok import get_aweme_id, get_data, get_redirect_url
from bot.utils import handle_images, handle_music, handle_video

base_router = Router()
url_router = Router()


@base_router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply("👋")
    await message.bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(0.7)
    await message.answer(
        "Привіт! Я допоможу тобі завантажити будь-яке відео, "
        "картинки та музику без водяного знаку. "
        "Просто відправ мені посилання з ТікТоку, а я тобі відправлю результат!"
    )


@url_router.message(F.text)
async def url_handler(message: Message):
    url: str | None = await get_redirect_url(message.text)

    if not url:
        logging.warning(
            f"The following text don't seem to be TikTok link.\nTEXT: [{message.text}]"
        )
        return await message.reply("Це не схоже на посилання ТікТок...")

    aweme_id: int | None = get_aweme_id(url)
    if not aweme_id:
        logging.warning(f"Failed to get Aweme ID.\nURL: [{message.text}]")
        return await message.reply(
            "При обробці вашого посилання сталася помилка. Перевірте посилання та спробуйте ще раз!"
        )

    data = await get_data(aweme_id)

    if "images" not in data:
        video_url: str = data["hdplay"]
        await handle_video(message, video_url)
    else:
        images: list[str] = data["images"]
        await handle_images(message, images)

    music_url = data["music"]
    await handle_music(message, music_url)


@url_router.error()
async def error_handler(event: ErrorEvent):
    await event.update.message.reply("Щось пішло не так...")
    raise event.exception
