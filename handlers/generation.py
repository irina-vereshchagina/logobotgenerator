from aiogram import types
from aiogram.fsm.context import FSMContext
from utils.states import GenerationStates
from utils.user_state import single_user_lock, is_generating, set_generating
from services.logo_generator import generate_image
from aiogram.types import BufferedInputFile
import logging

# 👇 добавили импорт для квот
from services.subscriptions import get_quotas, dec_gen


async def handle_idea(message: types.Message, state: FSMContext):
    # Получаем текущее состояние FSM
    state_now = await state.get_state()
    if state_now != GenerationStates.waiting_for_idea.state:
        print("[DEBUG] Пользователь не в состоянии ожидания идеи, игнорируем сообщение")
        return

    user_id = message.from_user.id

    if not message.text:
        await message.answer("❗️Ожидается текст с идеей логотипа. Пожалуйста, напишите словами.")
        return

    # 1) Проверка квот (вне блокировки)
    q = get_quotas(user_id)
    if q["gen_left"] <= 0:
        await message.answer("У тебя закончились генерации. Нажми «💎 Купить доступ» и пополни тариф.")
        return

    if is_generating(user_id):
        await message.answer("⏳ Пожалуйста, дождитесь завершения генерации логотипа.")
        return

    async with single_user_lock(user_id):
        # 2) Проверка квот повторно внутри блокировки (на случай гонки)
        q = get_quotas(user_id)
        if q["gen_left"] <= 0:
            await message.answer("У тебя закончились генерации. Нажми «💎 Купить доступ».")
            return

        set_generating(user_id, True)
        await message.answer("Генерирую логотип, подожди немного...")

        try:
            # Генерация
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")

            # 3) Списываем квоту только после успешной генерации
            if not dec_gen(user_id):
                await message.answer("⚠️ Не удалось списать генерацию с баланса. Напиши в поддержку.")
            else:
                left = get_quotas(user_id)
                await message.answer(
                    f"✅ Генерация выполнена.\n"
                    f"Осталось: {left['gen_left']} генераций, {left['vec_left']} векторизаций.\n"
                    f"💡 Пришли ещё идею или нажми '⬅️ В меню'."
                )

        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            set_generating(user_id, False)
