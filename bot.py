import os
import logging
import requests
from io import BytesIO
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import openai
from telegram.constants import ChatAction


# Загружаем токены из .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
openai.api_key = OPENAI_API_KEY

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, опиши идею для своего логотипа")

# Обработка текстовых сообщений
async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_idea = update.message.text

    await update.message.chat.send_action(action=ChatAction.TYPING)
    await update.message.reply_text("Генерирую логотип, подожди немного...")

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=user_idea,
            n=1,
            size="1024x1024",
            quality="standard",
            style="vivid",
        )
        image_url = response.data[0].url

        image_data = requests.get(image_url)
        image_data.raise_for_status()

        image_file = BytesIO(image_data.content)
        image_file.name = "logo.png"

        await update.message.reply_photo(photo=image_file, caption="Вот логотип по твоей идее!")

    except Exception as e:
        logging.exception("Ошибка при генерации изображения:")
        await update.message.reply_text(f"Произошла ошибка: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
