import asyncio
import os
import logging

from aiogram import Bot, Dispatcher

from src.bot.handlers import handlers_router


bot = Bot(token=os.getenv("BOT_TOKEN"))
dispatcher = Dispatcher()
dispatcher.include_router(handlers_router)


async def main() -> None:
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit bot")
