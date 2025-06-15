from aiogram import types
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU

async def info(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)
    await message.answer(
        "ℹ️ Генерация логотипов через GPT-4o + DALL·E 3.\n\n"
        "Жми '🎨 Генерация логотипа' и отправь идею.\n"
        "Или выбери другой режим ниже 👇",
        reply_markup=get_main_keyboard()
    )