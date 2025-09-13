# handlers/prompt.py
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards import get_back_keyboard
from utils.user_state import set_user_state, STATE_GENERATE
from utils.states import GenerationStates

router = Router()

@router.message(F.text == "🎨 Генерация логотипа")
async def prompt_for_idea(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_GENERATE)
    await state.set_state(GenerationStates.waiting_for_idea)
    await message.answer(
        "✍️ Отправь идею логотипа (например: «логотип для кофейни в минималистичном стиле»)",
        reply_markup=get_back_keyboard()
    )
