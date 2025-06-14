from aiogram import types
from aiogram.types import BufferedInputFile
from utils.user_state import single_user_lock
import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

# Флаг состояния — ждём изображение?
awaiting_image_users = set()

async def ask_for_image(message: types.Message):
    user_id = message.from_user.id
    awaiting_image_users.add(user_id)
    await message.answer("📤 Пожалуйста, пришли изображение для векторизации (JPG, PNG и т.д.).")

async def handle_vectorization_image(message: types.Message):
    user_id = message.from_user.id
    if user_id not in awaiting_image_users:
        return  # Игнорируем нецелевые изображения

    if not message.photo:
        await message.answer("❗️ Пожалуйста, отправьте именно изображение, не файл и не текст.")
        return

    async with single_user_lock(user_id):
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
            else:
                await message.answer(f"❌ Ошибка векторизации: {response.status_code}\n{response.text}")

        except Exception as e:
            logging.exception("Ошибка при векторизации")
            await message.answer(f"⚠️ Произошла ошибка: {e}")
        finally:
            awaiting_image_users.discard(user_id)
