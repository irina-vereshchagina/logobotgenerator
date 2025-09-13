# handlers/generation.py
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile
import logging

from utils.states import GenerationStates
from utils.user_state import single_user_lock, is_generating, set_generating
from services.logo_generator import generate_image
from services.subscriptions import get_quotas, dec_gen, ensure_free_quota
from config import FREE_GEN_TRIAL
from utils.user_state import STATE_GENERATE

router = Router()

@router.message(
    F.text & (F.text.as_("txt") != None)  # есть текст
)
async def handle_idea(message: types.Message, state: FSMContext):
    # обрабатываем только когда ждём идею
    if await state.get_state() != GenerationStates.waiting_for_idea.state:
        return

    user_id = message.from_user.id

    # выдаём бесплатные квоты, если новый пользователь
    ensure_free_quota(user_id, free_gen=FREE_GEN_TRIAL, free_vec=0)

    # проверка квот вне блокировки
    q = get_quotas(user_id)
    if q["gen_left"] <= 0:
        await message.answer("У тебя закончились генерации. Нажми «💎 Купить доступ» и пополни тариф.")
        return

    if is_generating(user_id):
        await message.answer("⏳ Подожди завершения текущей генерации.")
        return

    async with single_user_lock(user_id):
        # двойная проверка внутри блокировки
        q = get_quotas(user_id)
        if q["gen_left"] <= 0:
            await message.answer("У тебя закончились генерации. Нажми «💎 Купить доступ».")
            return

        set_generating(user_id, True)
        await message.answer("Генерирую логотип, подожди немного...")

        try:
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")

            # списываем квоту только при успехе
            if not dec_gen(user_id):
                await message.answer("⚠️ Не удалось списать генерацию. Напиши в поддержку.")
        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            set_generating(user_id, False)
