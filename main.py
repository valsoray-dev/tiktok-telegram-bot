import asyncio
import logging
from contextlib import suppress
from os import getenv

from aiogram import Bot, Dispatcher, loggers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from rich.logging import RichHandler

from bot.handlers import error_router, message_router, start_router

load_dotenv()


async def main() -> None:
    bot_token = getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN should be in .env")

    bot = Bot(bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_routers(error_router, message_router, start_router)

    # Sometimes, "I test in production" and users send messages when the bot is down.
    # Here I need to drop all updates, so the bot doesn't have to respond to messages
    # that were sent while the bot wasn't running.
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)  # type: ignore


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            # This bot is far from the most stable, so I need cool tracebacks
            RichHandler(rich_tracebacks=True, log_time_format="[%d/%m/%y %H:%M:%S]")
        ],
    )

    # disable annoying aiogram update info messages
    loggers.event.setLevel(logging.WARNING)

    with suppress(KeyboardInterrupt):
        asyncio.run(main())
