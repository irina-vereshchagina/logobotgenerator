import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation, vectorize
from handlers.vectorize import awaiting_image_users  # 👈 импорт множества

logging.basicConfig(level=logging.INFO)

defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher()


def is_text_and_not_in_vector_mode(message):
    return (
        message.text
        and not message.text.startswith("/")
        and message.from_user.id not in awaiting_image_users
    )


dp.message.register(start.start, CommandStart())
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(vectorize.ask_for_image, lambda m: m.text == "🖼 Векторизация")
dp.message.register(vectorize.handle_vectorization_image, lambda m: m.photo)
dp.message.register(generation.handle_idea, is_text_and_not_in_vector_mode)

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
