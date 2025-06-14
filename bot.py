import os
import asyncio
import logging
import random
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from io import BytesIO
from contextlib import asynccontextmanager

# Загрузка .env переменных
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher()

# Состояния пользователей
user_locks = {}
user_generation_flags = {}
user_svg_mode = set()  # Пользователи, ожидающие отправку изображения для SVG

# Клавиатура
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Генерация логотипа")],
            [KeyboardButton(text="🖼️ Image to SVG")],
            [KeyboardButton(text="ℹ️ Информация")],
        ],
        resize_keyboard=True
    )

@asynccontextmanager
async def single_user_lock(user_id: int):
    lock = user_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        yield

@dp.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип или перевести изображение в SVG.\n\nВыбери действие:",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda m: m.text == "ℹ️ Информация")
async def info(message: types.Message):
    await message.answer(
        "🔧 Возможности бота:\n"
        "— Генерация логотипов через GPT-4o + DALL·E 3\n"
        "— Конвертация изображений в вектор (SVG)\n\n"
        "Выбери нужное действие с помощью кнопок."
    )

@dp.message(lambda m: m.text == "🎨 Генерация логотипа")
async def prompt_for_idea(message: types.Message):
    await message.answer("✍️ Отправь идею логотипа (" +
                         "например: 'логотип для кофейни в минималистичном стиле')")

@dp.message(lambda m: m.text and m.from_user.id in user_svg_mode)
async def reject_text_in_svg_mode(message: types.Message):
    await message.answer("⚠️ Пожалуйста, отправьте изображение, а не текст.")

@dp.message(lambda m: m.text and not m.text.startswith("/") and m.from_user.id not in user_svg_mode)
async def handle_idea(message: types.Message):
    user_id = message.from_user.id

    if user_generation_flags.get(user_id, False):
        await message.answer("⏳ Пожалуйста, дождитесь завершения генерации логотипа.")
        return

    async with single_user_lock(user_id):
        user_generation_flags[user_id] = True
        await message.answer("🎨 Генерирую логотип, подожди немного...")
        try:
            image = await generate_image(message.text)
            image.seek(0)
            input_file = BufferedInputFile(file=image.read(), filename="logo.png")
            await message.answer_photo(photo=input_file, caption="Вот логотип по твоей идее!")
            await message.answer("💡 Пришли ещё идею для генерации логотипа!")
        except Exception as e:
            logging.exception("Ошибка при генерации")
            await message.answer(f"❌ Произошла ошибка: {e}")
        finally:
            user_generation_flags[user_id] = False

@dp.message(lambda m: m.text == "🖼️ Image to SVG")
async def image_to_svg_prompt(message: types.Message):
    user_id = message.from_user.id
    user_svg_mode.add(user_id)
    await message.answer("📤 Отправьте изображение, которое хотите перевести в вектор (SVG).")

@dp.message(lambda m: m.photo or m.document)
async def handle_svg_conversion(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_svg_mode:
        return

    try:
        file = message.photo[-1] if message.photo else message.document
        file_info = await bot.get_file(file.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"

        image_data = requests.get(file_url)
        image_data.raise_for_status()
        with open("temp_image.jpg", "wb") as f:
            f.write(image_data.content)

        response = requests.post(
            'https://ru.vectorizer.ai/api/v1/vectorize',
            files={'image': open('temp_image.jpg', 'rb')},
            data={'mode': 'test'},
            auth=(VECTORIZE_USER, VECTORIZE_PASS)
        )

        if response.status_code == 200:
            with open("result.svg", "wb") as out:
                out.write(response.content)
            with open("result.svg", "rb") as svg_file:
                await message.answer_document(BufferedInputFile(svg_file.read(), filename="result.svg"))
        else:
            await message.answer(f"❌ Ошибка при векторизации: {response.status_code}")

    except Exception as e:
        logging.exception("Ошибка при векторизации изображения")
        await message.answer("⚠️ Пожалуйста, отправьте корректное изображение (фото или файл).")

    finally:
        user_svg_mode.discard(user_id)
        try:
            os.remove("temp_image.jpg")
            os.remove("result.svg")
        except:
            pass

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
    asyncio.run(dp.start_polling(bot))