import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import API_TOKEN
from database import create_table
from handlers.quiz import router as quiz_router
from handlers.start import router as start_router

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Объект бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.include_router(quiz_router)
dp.include_router(start_router)


async def main():
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
