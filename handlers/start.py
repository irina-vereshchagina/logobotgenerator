from aiogram import types
from aiogram.filters import CommandStart
from keyboards import get_main_keyboard

async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )
