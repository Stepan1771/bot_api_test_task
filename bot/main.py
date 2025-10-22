import os

from dotenv import load_dotenv

from bot.setup import setup_handlers

import asyncio

from aiogram import Bot, Dispatcher, Router

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

async def main():

    dp = Dispatcher()
    bot = Bot(token=TOKEN)

    main_router = Router()
    dp.include_router(main_router)

    setup_handlers(main_router, bot)

    await dp.start_polling(bot)

if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")