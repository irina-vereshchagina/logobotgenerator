# handlers/vectorize.py
from aiogram import Router, types, F
from aiogram.types import BufferedInputFile
from keyboards import get_back_keyboard
from utils.user_state import single_user_lock, is_generating, set_generating, set_user_state, STATE_VECTORIZE
from services.subscriptions import get_quotas, dec_vec
import logging, os, requests
from dotenv import load_dotenv

load_dotenv()
VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

router = Router()

@router.message(F.text == "🖼 Векторизация")
async def ask_for_image(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_VECTORIZE)
    await message.answer(
        "📤 Пришли изображение для векторизации (JPG/PNG).",
        reply_markup=get_back_keyboard()
    )

@router.message(F.photo)
async def handle_vectorization_image(message: types.Message):
    user_id = message.from_user.id

    # проверка квот
    q = get_quotas(user_id)
    if q["vec_left"] <= 0:
        await message.answer("У тебя закончились векторизации. Нажми «💎 Купить доступ».")
        return

    if is_generating(user_id):
        await message.answer("⏳ Подожди завершения предыдущей операции.")
        return

    async with single_user_lock(user_id):
        q = get_quotas(user_id)
        if q["vec_left"] <= 0:
            await message.answer("У тебя закончились векторизации. Нажми «💎 Купить доступ».")
            return

        set_generating(user_id, True)
        try:
            photo = message.photo[-1]
            file = await message.bot.get_file(photo.file_id)
            downloaded = await message.bot.download_file(file.file_path)

            temp_path = f"temp_{user_id}.jpg"
            with open(temp_path, "wb") as f:
                f.write(downloaded.read())

            await message.answer("🔄 Векторизую изображение, подождите...")

            with open(temp_path, "rb") as img:
                resp = requests.post(
                    "https://ru.vectorizer.ai/api/v1/vectorize",
                    files={"image": img},
                    data={"mode": "test"},
                    auth=(VECTORIZE_USER, VECTORIZE_PASS),
                    timeout=120
                )
            try:
                os.remove(temp_path)
            except Exception:
                pass

            if resp.status_code == 200:
                svg_path = f"vectorized_{user_id}.svg"
                with open(svg_path, "wb") as f:
                    f.write(resp.content)
                with open(svg_path, "rb") as f:
                    svg_file = BufferedInputFile(file=f.read(), filename="vectorized.svg")
                    await message.answer_document(svg_file, caption="✅ Векторизация завершена!")
                try:
                    os.remove(svg_path)
                except Exception:
                    pass

                # списываем квоту только при успехе
                dec_vec(user_id)
            else:
                await message.answer(f"❌ Ошибка векторизации: {resp.status_code}\n{resp.text}")

        except requests.Timeout:
            logging.exception("Таймаут векторизации")
            await message.answer("⏱️ Сервис векторизации ответил слишком долго. Попробуй позже.")
        except Exception as e:
            logging.exception("Ошибка при векторизации")
            await message.answer(f"⚠️ Произошла ошибка: {e}")
        finally:
            set_generating(user_id, False)
