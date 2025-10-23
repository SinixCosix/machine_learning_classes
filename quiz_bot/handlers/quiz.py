from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.context import FSMContext
from data.quiz_data import quiz_data
from database import update_quiz_index, get_quiz_index, save_quiz
from keyboards.builders import generate_options_keyboard

from quiz_bot.database import get_quiz_statistics
from quiz_bot.keyboards.builders import get_finish_keyboard, get_start_keyboard
from states import Quiz

router = Router()


@router.message(Command("start"))
@router.message(F.text == "Начать игру")
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в квиз!", reply_markup=get_start_keyboard())
    await new_quiz(message, state)


@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    await message.answer("Давайте начнем квиз!")
    await new_quiz(message, state)


@router.callback_query(F.data.contains("right_answer"))
async def right_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    user_answer = callback.data.split('.')[1]

    qd = await state.get_data()
    qd = qd['quiz_data']
    qd.append({
        'answer': user_answer,
        'is_correct': True,
    })
    await state.update_data(quiz_data=qd)
    await callback.message.edit_text(f"Верно! Ваш ответ: {user_answer}")
    await next_or_finish(callback, current_question_index, state)


@router.callback_query(F.data.contains("wrong_answer"))
async def wrong_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    user_answer = callback.data.split('.')[1]
    correct_option = quiz_data[current_question_index]['correct_option']
    qd = await state.get_data()
    qd = qd['quiz_data']
    qd.append({
        'answer': user_answer,
        'is_correct': False,
    })
    await state.update_data(quiz_data=qd)
    await callback.message.edit_text(
        f"Неправильно.  Ваш ответ: {user_answer}. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")
    await next_or_finish(callback, current_question_index, state)


@router.callback_query(F.data == "finish_quiz")
async def finish_quiz(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Quiz.finish)
    await callback.message.answer("Это был последний вопрос. Квиз завершен!", reply_markup=get_finish_keyboard())


# Вспомогательные функции (не являются хэндлерами)
async def new_quiz(message, state: FSMContext):
    user_id = message.from_user.id
    current_question_index = 0
    await state.update_data(quiz_data=[])
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id, state)


async def get_question(message, user_id, state: FSMContext):
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']

    kb = generate_options_keyboard(opts, opts[correct_index])
    await state.set_state(Quiz.question)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def next_or_finish(callback: types.CallbackQuery, current_question_index, state: FSMContext):
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id, state)
    else:
        await finish_quiz(callback, state)


@router.callback_query(F.data == 'show_user_answers')
async def show_user_answers(callback: types.CallbackQuery, state: FSMContext):
    qd = await state.get_data()
    qd = qd['quiz_data']
    text = 'Ваши ответы:\n\n'

    i = 1
    for answer in qd:
        text += f"{i}. Верно: {'Да' if answer['is_correct'] else 'Нет'}. Ваш ответ '{answer['answer']}'"
        i += 1

    await callback.message.edit_text(text, reply_markup=get_finish_keyboard())


@router.callback_query(F.data == 'save_quiz')
async def handle_save_quiz(callback: types.CallbackQuery, state: FSMContext):
    qd = await state.get_data()
    qd = qd['quiz_data']
    await save_quiz(callback.from_user.id, qd)
    await callback.answer('Сохранено', reply_markup=get_finish_keyboard())


@router.message(F.text == '6. Статистика')
async def handle_show_statistics(message: types.Message):
    try:
        stats = await get_quiz_statistics()

        message_text = "📊 <b>Статистика квиза</b>\n\n"

        message_text += f"👥 <b>Всего игроков:</b> {stats['total_players']}\n"
        message_text += f"📝 <b>Всего ответов:</b> {stats['total_answers']}\n"
        message_text += f"✅ <b>Правильных ответов:</b> {stats['correct_answers']}\n"
        message_text += f"📈 <b>Процент правильных:</b> {stats['correct_percentage']}%\n\n"

        if stats.get('hardest_question'):
            message_text += f"🔥 <b>Самый сложный вопрос:</b> №{stats['hardest_question']['index']}\n"
            message_text += f"   (успешно: {stats['hardest_question']['success_rate']}%)\n"

        if stats.get('easiest_question'):
            message_text += f"🎯 <b>Самый легкий вопрос:</b> №{stats['easiest_question']['index']}\n"
            message_text += f"   (успешно: {stats['easiest_question']['success_rate']}%)\n\n"

        if stats['top_players']:
            message_text += "🏆 <b>Топ-5 игроков:</b>\n"
            for i, (user_id, correct_answers) in enumerate(stats['top_players'], 1):
                message_text += f"{i}. ID {user_id}: {correct_answers} правильных ответов\n"
        else:
            message_text += "🏆 <b>Топ игроков:</b> пока нет данных\n"

        await message.answer(message_text, parse_mode='HTML')

    except Exception as e:
        error_message = "❌ Произошла ошибка при получении статистики. Попробуйте позже."
        await message.answer(error_message)
        print(f"Error in statistics: {e}")