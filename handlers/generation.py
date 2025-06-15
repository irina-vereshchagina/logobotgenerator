from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.states import GenerationStates
from utils.user_state import single_user_lock, is_generating, set_generating
from services.logo_generator import generate_image
from aiogram.types import BufferedInputFile
import logging
from utils.user_roles import can_generate, increment_usage

async def handle_idea(message: types.Message, state: FSMContext):
    state_now = await state.get_state()
    if state_now != GenerationStates.waiting_for_idea.state:
        return

    user_id = message.from_user.id

    if not message.text:
        await message.answer("❗️Ожидается текст с идеей логотипа.")
        return

    if not can_generate(user_id):
        await message.answer("❌ Вы исчерпали лимит генераций для вашей роли.")
        return

    if is_generating(user_id):
        await message.answer("⏳ Пожалуйста, дождитесь завершения генерации логотипа.")
        return

    async with single_user_lock(user_id):
        set_generating(user_id, True)
        await message.answer("Генерирую логотип, подожди немного...")
        try:
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")
            await message.answer("💡 Пришли ещё идею или нажми '⬅️ В меню'.")
            increment_usage(user_id, "generations")
        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            set_generating(user_id, False)
