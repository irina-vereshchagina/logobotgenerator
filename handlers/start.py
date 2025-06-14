from aiogram import types
from aiogram.filters import CommandStart
from keyboards import get_main_keyboard
from handlers.vectorize import awaiting_image_users

async def start(message: types.Message):
    user_id = message.from_user.id
    awaiting_image_users.discard(user_id)
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )
