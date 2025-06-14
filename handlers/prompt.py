from aiogram import types
from keyboards import get_back_keyboard
from handlers.vectorize import awaiting_image_users

async def prompt_for_idea(message: types.Message):
    user_id = message.from_user.id
    awaiting_image_users.discard(user_id)  # выходим из режима векторизации
    await message.answer(
        "✍️ Отправь идею логотипа (например: 'логотип для кофейни в минималистичном стиле')",
        reply_markup=get_back_keyboard()
    )
