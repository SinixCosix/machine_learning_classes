from aiogram.fsm.state import StatesGroup, State


class Quiz(StatesGroup):
    question = State()
    finish = State()