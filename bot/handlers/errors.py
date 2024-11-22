from typing import NoReturn
from aiogram import Router
from aiogram.types import ErrorEvent

error_router = Router()


@error_router.error()
async def error_handler(event: ErrorEvent) -> NoReturn:
    if event.update.message is not None:
        await event.update.message.reply("Щось пішло не так...")
    raise event.exception
