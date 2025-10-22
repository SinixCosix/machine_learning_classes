import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F

from config import API_TOKEN
from database import create_table
from handlers.start import cmd_start
from handlers.quiz import cmd_quiz, right_answer, wrong_answer, new_quiz

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Объект бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрируем хэндлеры
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_start, F.text == "Начать игру")
dp.message.register(cmd_quiz, Command("quiz"))
dp.message.register(new_quiz, F.text == "Начать игру")
dp.callback_query.register(right_answer, F.data == "right_answer")
dp.callback_query.register(wrong_answer, F.data == "wrong_answer")


async def main():
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
