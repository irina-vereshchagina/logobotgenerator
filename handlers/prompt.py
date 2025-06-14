from aiogram import types
from keyboards import get_back_keyboard
from utils.user_state import set_user_state, STATE_GENERATE

async def prompt_for_idea(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_GENERATE)
    await message.answer(
        "✍️ Отправь идею логотипа (например: 'логотип для кофейни в минималистичном стиле')",
        reply_markup=get_back_keyboard()
    )
