import os
import logging
import requests
from io import BytesIO
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
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

# === OpenAI клиент ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === Пользовательское состояние генерации ===
user_states = {}

# === Генерация кнопок ===
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎨 Генерация логотипа")],
            [KeyboardButton("ℹ️ Информация")],
        ],
        resize_keyboard=True,
    )

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = {"busy": False}
    await update.message.reply_text(
        "Привет! Я помогу тебе сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard(),
    )

# === Информация ===
async def handle_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я генерирую логотипы с помощью GPT-4o и DALL·E 3. Просто выбери '🎨 Генерация логотипа' и опиши идею, например:\n\n"
        "👉 'Логотип для кофейни в минималистичном стиле'\n\n"
        "Обычно генерация занимает 10–15 секунд.",
    )

# === Генерация изображения (GPT + DALL·E) ===
async def generate_image(user_prompt: str) -> BytesIO:
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

    image_response = client.images.generate(
        model="dall-e-3",
        prompt=improved_prompt,
        n=1,
        size="1024x1024",
        quality="standard",
        style="vivid",
    )

    image_url = image_response.data[0].url
    image_data = requests.get(image_url)
    image_data.raise_for_status()

    image_file = BytesIO(image_data.content)
    image_file.name = "logo.png"
    return image_file

# === Основной обработчик логотипа ===
async def handle_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_states:
        user_states[user_id] = {"busy": False}

    # Обработка кнопок
    if text == "ℹ️ Информация":
        return await handle_info(update, context)

    if text == "🎨 Генерация логотипа":
        await update.message.reply_text("Отправь мне текстовую идею для логотипа (например: 'логотип для магазина книг').")
        return

    # Защита от повторных запросов
    if user_states[user_id]["busy"]:
        await update.message.reply_text("⏳ Генерация логотипа в процессе. Пожалуйста, подожди...")
        return

    user_states[user_id]["busy"] = True

    try:
        await update.message.chat.send_action(action=ChatAction.TYPING)
        await update.message.reply_text("Генерирую логотип, подожди немного...")

        image_file = await generate_image(text)
        await update.message.reply_photo(photo=image_file, caption="Вот логотип по твоей идее!")

    except Exception as e:
        logging.exception("Ошибка при генерации:")
        await update.message.reply_text(f"Произошла ошибка при генерации: {e}")
    finally:
        user_states[user_id]["busy"] = False

# === Запуск бота ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_idea))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
