# handlers/start.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU

router = Router()

@router.message(CommandStart())
@router.message(F.text == "⬅️ В меню")
async def start(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )
