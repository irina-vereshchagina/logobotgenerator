import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation, vectorize, payments
from keyboards import get_pay_keyboard
from utils.user_state import get_user_state, STATE_GENERATE, STATE_VECTORIZE, STATE_MENU

logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher(storage=MemoryStorage())

def is_generate_text(message):
    return (
        message.text and not message.text.startswith("/")
        and get_user_state(message.from_user.id) == STATE_GENERATE
    )

def is_vectorization_photo(message):
    return (
        message.photo
        and get_user_state(message.from_user.id) == STATE_VECTORIZE
    )

# --- твои текущие хэндлеры ---
dp.message.register(start.start, CommandStart())
dp.message.register(start.start, lambda m: m.text == "⬅️ В меню")
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(vectorize.ask_for_image, lambda m: m.text == "🖼 Векторизация")
dp.message.register(vectorize.handle_vectorization_image, is_vectorization_photo)
dp.message.register(generation.handle_idea, is_generate_text)

# --- показать кнопку оплаты при нажатии "💎 Купить доступ" (Reply-кнопка из меню) ---
async def show_pay(message):
    await message.answer(
        "Чтобы продолжить, оплати 500⭐:",
        reply_markup=get_pay_keyboard()
    )
dp.message.register(show_pay, lambda m: m.text == "💎 Купить доступ")

# --- подключаем роутер оплат (обрабатывает нажатие inline-кнопки и сам платёж) ---
dp.include_router(payments.router)

# --- фолбек ---
@dp.message()
async def fallback_handler(message):
    state = get_user_state(message.from_user.id)
    if state == STATE_MENU:
        await message.answer("❗️Вы сейчас в главном меню. Пожалуйста, выберите действие кнопкой ниже.")
    elif state == STATE_GENERATE:
        await message.answer("❗️Ожидается текстовая идея логотипа.")
    elif state == STATE_VECTORIZE:
        await message.answer("❗️Ожидается изображение (фото) для векторизации.")
    else:
        await message.answer("❓ Непонятное состояние. Нажмите '⬅️ В меню'.")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
