from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.states import GenerationStates

async def prompt_for_idea(message: types.Message, state: FSMContext):
    await state.set_state(GenerationStates.waiting_for_idea)
    await message.answer(
        "✍️ Отправь идею логотипа (например: 'логотип для кофейни в минималистичном стиле')"
    )
