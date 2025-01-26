import logging
from typing import NoReturn

from aiogram import F, Router
from aiogram.types import ErrorEvent, Message

error_router = Router()


@error_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message) -> NoReturn:
    """Handle all errors that was not caught."""
    await message.reply("Щось пішло не так... Спробуйте ще раз!")
    logging.error("Something went wrong.\nMessage: [%s]", message.text)
    raise event.exception
