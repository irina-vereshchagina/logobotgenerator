from aiogram import types

async def info(message: types.Message):
    await message.answer(
        "Генерация логотипов через GPT-4o + DALL·E 3.\n\n"
        "Жми '🎨 Генерация логотипа' и отправь идею."
    )
