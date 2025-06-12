import os
import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from io import BytesIO
from contextlib import asynccontextmanager

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

logging.basicConfig(level=logging.INFO)

defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher()

user_locks = {}
user_generation_flags = {}
user_vectorize_flags = {}
user_waiting_for_image = set()

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Генерация логотипа")],
            [KeyboardButton(text="🧹 Векторизовать изображение")],
            [KeyboardButton(text="ℹ️ Информация")],
        ],
        resize_keyboard=True
    )

@asynccontextmanager
async def single_user_lock(user_id: int):
    lock = user_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        yield

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип или векторизовать картинку.",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda m: m.text == "ℹ️ Информация")
async def info(message: types.Message):
    await message.answer(
        "Генерация логотипов через GPT-4o + DALL·E 3\nВекторизация картинок через vectorizer.ai."
    )

@dp.message(lambda m: m.text == "🎨 Генерация логотипа")
async def prompt_for_idea(message: types.Message):
    await message.answer("✍️ Отправь идею логотипа")

@dp.message(lambda m: m.text == "🧹 Векторизовать изображение")
async def start_vectorization(message: types.Message):
    user_id = message.from_user.id
    if user_vectorize_flags.get(user_id, False):
        await message.answer("⏳ Подождите, векторизация уже выполняется.")
        return
    user_waiting_for_image.add(user_id)
    await message.answer("📷 Пришли изображение (файл) для векторизации.")

@dp.message(lambda m: m.document or m.photo)
async def handle_image_upload(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_waiting_for_image:
        return
    user_waiting_for_image.remove(user_id)
    user_vectorize_flags[user_id] = True
    await message.answer("⚙️ Векторизация запущена, подожди немного...")
    try:
        file = message.document or message.photo[-1]
        file_info = await bot.get_file(file.file_id)
        file_data = await bot.download_file(file_info.file_path)
        image_path = f"/tmp/{file.file_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(file_data.read())
        svg_path = await vectorize_image(image_path)
        with open(svg_path, "rb") as svg_file:
            input_file = BufferedInputFile(file=svg_file.read(), filename="vectorized.svg")
            await message.answer_document(document=input_file, caption="✅ Векторизация завершена!")
    except Exception as e:
        logging.exception("Ошибка при векторизации")
        await message.answer(f"⚠️ Ошибка: {e}")
    finally:
        user_vectorize_flags[user_id] = False

@dp.message(lambda m: m.text and not m.text.startswith("/"))
async def handle_idea(message: types.Message):
    user_id = message.from_user.id
    if user_generation_flags.get(user_id, False):
        await message.answer("⏳ Пожалуйста, дождитесь завершения генерации логотипа.")
        return
    async with single_user_lock(user_id):
        user_generation_flags[user_id] = True
        await message.answer("Генерирую логотип, подожди немного...")
        try:
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")
        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"Произошла ошибка: {e}")
        finally:
            user_generation_flags[user_id] = False

async def generate_image(prompt: str) -> BytesIO:
    if USE_PLACEHOLDER:
        await asyncio.sleep(2)
        url = "https://picsum.photos/1024"
        response = requests.get(url)
        response.raise_for_status()
        image = BytesIO(response.content)
        image.name = "logo.png"
        return image
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    chat = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты создаешь промпт для генерации логотипа через DALL·E 3."},
            {"role": "user", "content": prompt}
        ]
    )
    prompt_dalle = chat.choices[0].message.content.strip()
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt_dalle,
        n=1,
        size="1024x1024",
        quality="standard",
        style="vivid",
    )
    image_url = image_response.data[0].url
    img_data = requests.get(image_url)
    img_data.raise_for_status()
    image = BytesIO(img_data.content)
    image.name = "logo.png"
    return image

async def vectorize_image(image_path: str) -> str:
    with open(image_path, 'rb') as img_file:
        response = requests.post(
            'https://ru.vectorizer.ai/api/v1/vectorize',
            files={'image': img_file},
            data={'mode': 'test'},
            auth=(VECTORIZE_USER, VECTORIZE_PASS)
        )
    if response.status_code == requests.codes.ok:
        result_path = image_path.replace(".jpg", ".svg")
        with open(result_path, 'wb') as out:
            out.write(response.content)
        return result_path
    else:
        raise Exception(f"Ошибка от vectorizer.ai: {response.status_code} {response.text}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
