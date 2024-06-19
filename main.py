import asyncio
import logging
from contextlib import suppress
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from rich.logging import RichHandler

from bot.handlers import base_router, url_router

load_dotenv()

TOKEN = getenv("BOT_TOKEN")


async def main() -> None:
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(base_router, url_router)

    # This bot is running on my home Linux server.
    # Sometimes, "I test in production" and
    # users send messages when the bot is down.
    # Here I need to drop all updates, so
    # the bot doesn't have to respond to messages
    # that were sent while the bot wasn't running.
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            # This bot is far from the most stable, so I need cool tracebacks
            RichHandler(rich_tracebacks=True)
        ],
    )
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
