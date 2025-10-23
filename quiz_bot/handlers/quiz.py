from aiogram import types
from aiogram.filters import Command
from aiogram import F
from data.quiz_data import quiz_data
from database import update_quiz_index, get_quiz_index
from keyboards.builders import generate_options_keyboard

from quiz_bot.keyboards.builders import get_finish_keyboard


async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']

    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    user_answer = quiz_data[current_question_index]['options'][correct_option]

    await callback.message.edit_text(f"Верно! Ваш ответ: {user_answer}")
    await next_or_finish(callback, current_question_index)


async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.edit_text(
        f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    await next_or_finish(callback, current_question_index)


async def next_or_finish(callback: types.CallbackQuery, current_question_index):
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await finish_quiz(callback)


async def finish_quiz(callback: types.CallbackQuery):
    await callback.message.answer("Это был последний вопрос. Квиз завершен!", reply_markup=get_finish_keyboard())
