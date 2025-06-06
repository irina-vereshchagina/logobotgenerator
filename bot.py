import os
import asyncio
import logging
import random
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from io import BytesIO
from contextlib import asynccontextmanager

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher()

# Хранилище блокировок и флагов пользователей
user_locks = {}
user_generation_flags = {}  # user_id -> bool

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Генерация логотипа")],
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
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda m: m.text == "ℹ️ Информация")
async def info(message: types.Message):
    await message.answer(
        "Генерация логотипов через GPT-4o + DALL·E 3.\n\n"
        "Жми '🎨 Генерация логотипа' и отправь идею."
    )

@dp.message(lambda m: m.text == "🎨 Генерация логотипа")
async def prompt_for_idea(message: types.Message):
    await message.answer(
        "✍️ Отправь идею логотипа (например: 'логотип для кофейни в минималистичном стиле')",
    )

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
            await message.answer("💡 Пришли ещё идею для генерации логотипа!")
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

if __name__ == "__main__":
    import asyncio

    asyncio.run(dp.start_polling(bot))