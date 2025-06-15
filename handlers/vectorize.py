from aiogram import types
from aiogram.types import BufferedInputFile
from keyboards import get_back_keyboard
from utils.user_state import single_user_lock, is_generating, set_generating, set_user_state, STATE_VECTORIZE
import logging
import os
import requests
from dotenv import load_dotenv
from utils.user_roles import can_vectorize, increment_usage

load_dotenv()

VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

async def ask_for_image(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_VECTORIZE)
    await message.answer("📤 Пришли изображение для векторизации.", reply_markup=get_back_keyboard())

async def handle_vectorization_image(message: types.Message):
    user_id = message.from_user.id

    if not can_vectorize(user_id):
        await message.answer("❌ Вы исчерпали лимит векторизаций для вашей роли.")
        return

    if is_generating(user_id):
        await message.answer("⏳ Пожалуйста, дождитесь завершения векторизации.")
        return

    async with single_user_lock(user_id):
        set_generating(user_id, True)
        try:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            downloaded_file = await message.bot.download_file(file.file_path)

            temp_path = f"temp_{user_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(downloaded_file.read())

            await message.answer("🔄 Векторизую изображение, подождите...")

            with open(temp_path, "rb") as img:
                response = requests.post(
                    'https://ru.vectorizer.ai/api/v1/vectorize',
                    files={'image': img},
                    data={'mode': 'test'},
                    auth=(VECTORIZE_USER, VECTORIZE_PASS)
                )

            os.remove(temp_path)

            if response.status_code == 200:
                svg_path = f"vectorized_{user_id}.svg"
                with open(svg_path, "wb") as f:
                    f.write(response.content)

                with open(svg_path, "rb") as f:
                    svg_file = BufferedInputFile(file=f.read(), filename="vectorized.svg")
                    await message.answer_document(document=svg_file, caption="✅ Векторизация завершена!")
                os.remove(svg_path)
                increment_usage(user_id, "vectorizations")
            else:
                await message.answer(f"❌ Ошибка векторизации: {response.status_code}\n{response.text}")

        except Exception as e:
            logging.exception("Ошибка при векторизации")
            await message.answer(f"⚠️ Произошла ошибка: {e}")
        finally:
            set_generating(user_id, False)
