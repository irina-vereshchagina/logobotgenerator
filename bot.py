from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation
from aiogram.filters import CommandStart
from utils.states import GenerationStates

# FSM хранилище
dp = Dispatcher(storage=MemoryStorage())

# Регистрация хендлеров
dp.message.register(start.start, CommandStart())
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(generation.handle_idea, GenerationStates.waiting_for_idea)
