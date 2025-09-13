import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers.start import router as start_router
from handlers.info import router as info_router
from handlers.prompt import router as prompt_router
from handlers.generation import router as generation_router
from handlers.vectorize import router as vectorize_router
from keyboards import get_main_keyboard  # понадобится для фолбэка
from utils.user_state import (
    get_user_state,
    STATE_GENERATE,
    STATE_VECTORIZE,
    STATE_MENU,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.INFO)


async def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in .env")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры с хендлерами
    dp.include_router(start_router)
    dp.include_router(info_router)
    dp.include_router(prompt_router)
    dp.include_router(generation_router)
    dp.include_router(vectorize_router)

    # Фолбэк‑хендлер для сообщений, которые не подошли ни под один другой хендлер
    @dp.message()
    async def fallback_handler(message: types.Message):
        state = get_user_state(message.from_user.id)
        if state == STATE_MENU:
            # В главном меню показываем клавиатуру заново
            await message.answer(
                "❗️Вы сейчас в главном меню. Пожалуйста, выберите действие кнопкой ниже.",
                reply_markup=get_main_keyboard(),
            )
        elif state == STATE_GENERATE:
            await message.answer("❗️Ожидается текстовая идея логотипа.")
        elif state == STATE_VECTORIZE:
            await message.answer("❗️Ожидается изображение (фото) для векторизации.")
        else:
            await message.answer("❓ Непонятное состояние. Нажмите '⬅️ В меню'.")

    # Запуск polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
