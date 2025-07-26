import logging
from html import escape
from typing import NoReturn

from aiogram import Bot, F, Router, html
from aiogram.types import ErrorEvent, Message

from bot.config import OWNER_ID

logger = logging.getLogger(__name__)


error_router = Router()


@error_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message, bot: Bot) -> NoReturn:
    """Handle all errors that was not caught."""
    await message.reply("Щось пішло не так... Спробуйте ще раз!")
    logger.error("Something went wrong.\nMessage: [%s]", message.text)
    await bot.send_message(
        chat_id=OWNER_ID,
        text=html.pre_language(escape(repr(event.exception)), "python"),
    )
    raise event.exception
