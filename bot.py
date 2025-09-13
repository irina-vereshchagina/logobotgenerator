
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers.start import router as start_router
from handlers.info import router as info_router
from handlers.prompt import router as prompt_router
from handlers.generation import router as generation_router
from handlers.vectorize import router as vectorize_router

logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.INFO)

async def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN в .env")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Подключаем все роутеры
    dp.include_router(start_router)
    dp.include_router(info_router)
    dp.include_router(prompt_router)
    dp.include_router(generation_router)
    dp.include_router(vectorize_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
