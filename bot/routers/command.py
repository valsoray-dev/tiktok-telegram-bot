import asyncio

from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

command_router = Router()


@command_router.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    await message.reply("👋")
    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(0.7)
    await message.answer(
        "Привіт! Я допоможу тобі завантажити будь-яке відео, "
        "картинки та музику без водяного знаку. "
        "Просто відправ мені посилання з ТікТоку, а я тобі відправлю результат!"
    )
