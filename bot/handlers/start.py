import asyncio

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router()


@start_router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply("👋")
    await message.bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(0.7)
    await message.answer(
        "Привіт! Я допоможу тобі завантажити будь-яке відео, "
        "картинки та музику без водяного знаку. "
        "Просто відправ мені посилання з ТікТоку, а я тобі відправлю результат!"
    )
