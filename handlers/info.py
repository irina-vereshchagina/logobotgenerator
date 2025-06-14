from aiogram import types
from keyboards import get_main_keyboard
from handlers.vectorize import awaiting_image_users

async def info(message: types.Message):
    user_id = message.from_user.id
    awaiting_image_users.discard(user_id)  # сбрасываем режим векторизации
    await message.answer(
        "ℹ️ Генерация логотипов через GPT-4o + DALL·E 3.\n\n"
        "Жми '🎨 Генерация логотипа' и отправь идею.\n"
        "Или выбери другой режим ниже 👇",
        reply_markup=get_main_keyboard()
    )
