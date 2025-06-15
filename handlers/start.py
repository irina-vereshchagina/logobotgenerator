from aiogram import types
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU

async def start(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )