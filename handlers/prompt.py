from aiogram import types

async def prompt_for_idea(message: types.Message):
    await message.answer(
        "✍️ Отправь идею логотипа (например: 'логотип для кофейни в минималистичном стиле')",
    )
