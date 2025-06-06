import os
import logging
import requests
import asyncio
from io import BytesIO
from dotenv import load_dotenv
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# === Этапы диалога ===
WAITING_FOR_IDEA = 1

# === Загрузка .env ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER") == "True"

# === Логирование ===
logging.basicConfig(level=logging.INFO)

# === Хранилище генераций ===
active_generations = set()  # user_ids в процессе генерации

# === Кнопки ===
def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🎨 Генерация логотипа")],
            [KeyboardButton("ℹ️ Информация")],
        ],
        resize_keyboard=True,
    )

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу тебе сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard(),
    )
    return ConversationHandler.END

# === Информация ===
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я генерирую логотипы с помощью GPT-4o и DALL·E 3.\n\n"
        "Нажми '🎨 Генерация логотипа' и отправь идею, например:\n"
        "👉 'логотип для кофейни в минималистичном стиле'"
    )
    return ConversationHandler.END

# === Заглушка / генерация ===
async def generate_image(user_prompt: str) -> BytesIO:
    if USE_PLACEHOLDER:
        await asyncio.sleep(5)
        url = "https://picsum.photos/1024"
        response = requests.get(url)
        response.raise_for_status()
        image_file = BytesIO(response.content)
        image_file.name = "logo.png"
        return image_file

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

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

# === Обработка кнопки "Генерация логотипа" ===
async def request_logo_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь идею логотипа (например: 'логотип для книжного магазина в минималистичном стиле').",
        reply_markup=ReplyKeyboardRemove(),
    )
    return WAITING_FOR_IDEA

# === Обработка идеи ===
async def handle_logo_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_prompt = update.message.text.strip()

    if user_id in active_generations:
        await update.message.reply_text("⏳ Генерация уже идёт. Подожди немного...")
        return WAITING_FOR_IDEA

    active_generations.add(user_id)
    await update.message.chat.send_action(action=ChatAction.TYPING)
    await update.message.reply_text("Генерирую логотип, подожди немного...")

    try:
        image = await generate_image(user_prompt)
        await update.message.reply_photo(photo=image, caption="Вот логотип по твоей идее!")
    except Exception as e:
        logging.exception("Ошибка при генерации:")
        await update.message.reply_text(f"Произошла ошибка: {e}")
    finally:
        active_generations.discard(user_id)

    await update.message.reply_text("Хочешь сгенерировать ещё? Выбери действие:", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# === Прерывание ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, возвращаю в меню.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# === Запуск бота ===
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎨 Генерация логотипа$"), request_logo_idea)],
        states={
            WAITING_FOR_IDEA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logo_idea),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ Информация$"), info))
    app.add_handler(conv)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
