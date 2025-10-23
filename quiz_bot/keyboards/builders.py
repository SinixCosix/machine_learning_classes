from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"right_answer.{option}" if option == right_answer else f"wrong_answer.{option}")
        )

    builder.adjust(1)
    return builder.as_markup()


def get_start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    return builder.as_markup(resize_keyboard=True)

def get_finish_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text='5. Вывести ответы',
        callback_data="show_user_answers",
    ))
    builder.add(types.InlineKeyboardButton(
        text='6. Статистика',
        callback_data="show_statistics",
    ))
    builder.add(types.InlineKeyboardButton(
        text="6. Сохранить",
        callback_data="save_quiz",
    ))

    return builder.as_markup(resize_keyboard=True)