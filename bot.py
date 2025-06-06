import os
import logging
import requests
from io import BytesIO
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# === Загрузка переменных окружения ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Инициализация OpenAI клиента ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Опиши идею логотипа (например: 'логотип кофейни в минималистичном стиле с тёплыми цветами'), "
        "и я пришлю тебе сгенерированное изображение."
    )

# === Генерация изображения (GPT + DALL·E 3) ===
async def generate_image(user_prompt: str) -> BytesIO:
    # GPT-4o формирует чёткий промпт
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты создаёшь визуально точные, детализированные описания изображений для DALL·E 3. "
                    "Твоя задача — превратить пользовательский запрос в качественный промпт для генерации логотипа."
                )
            },
            {
                "role": "user",
                "content": f"Сформулируй промпт для DALL·E 3: {user_prompt}"
            }
        ],
        temperature=0.7
    )

    improved_prompt = chat_response.choices[0].message.content.strip()

    # Генерация изображения DALL·E 3
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=improved_prompt,
        n=1,
        size="1024x1024",  # Можно изменить на 1792x1024 или 1024x1792 при необходимости
        quality="standard",
        style="vivid",
    )

    image_url = image_response.data[0].url
    image_data = requests.get(image_url)
    image_data.raise_for_status()

    image_file = BytesIO(image_data.content)
    image_file.name = "logo.png"
    return image_file

# === Обработка текстовых сообщений ===
async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_idea = update.message.text

    await update.message.chat.send_action(action=ChatAction.TYPING)
    await update.message.reply_text("Генерирую логотип, подожди немного...")

    try:
        image_file = await generate_image(user_idea)
        await update.message.reply_photo(photo=image_file, caption="Вот логотип по твоей идее!")
    except Exception as e:
        logging.exception("Ошибка при генерации изображения:")
        await update.message.reply_text(f"Произошла ошибка: {e}")

# === Точка входа ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
