from aiogram import F
from aiogram import Router, types
from aiogram.filters import Command

from keyboards.builders import get_start_keyboard

router = Router()

@router.message(Command("start"))
@router.message(F.text == "Начать игру")
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=get_start_keyboard())