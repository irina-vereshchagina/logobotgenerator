import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart

from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation
from utils.states import GenerationStates

logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher(storage=MemoryStorage())

dp.message.register(start.start, CommandStart())
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(generation.handle_idea, GenerationStates.waiting_for_idea)

if __name__ == "__main__":
    async def main():
        print("🔄 Запуск бота...")
        await dp.start_polling(bot)
    asyncio.run(main())
