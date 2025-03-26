import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher, loggers
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from rich.logging import RichHandler

from bot.config import BOT_TOKEN
from bot.routers import command_router, error_router, message_router


async def main() -> None:
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    dp.include_routers(command_router, error_router)

    # this router should be the last one
    dp.include_router(message_router)

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
