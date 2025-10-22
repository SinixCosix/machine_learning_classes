from aiogram import types
from aiogram.filters import Command
from aiogram import F
from keyboards.builders import get_start_keyboard

async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=get_start_keyboard())