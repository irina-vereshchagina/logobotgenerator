import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# --- Основные ключи ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Для векторизации (если используешь внешний сервис)
VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

# Включает использование заглушек вместо OpenAI (для тестов)
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

# --- Настройки тарифов ---
# Цены тарифов в Telegram Stars (или другой валюте, если поменяешь)
PLAN_PRICES = {
    "start": 500,
    "standard": 1000,
    "pro": 1500,
}

# Квоты генераций/векторизаций для каждого тарифа
PLAN_QUOTAS = {
    "start": {"gen": 10, "vec": 0},
    "standard": {"gen": 15, "vec": 1},
    "pro": {"gen": 30, "vec": 3},
}

# Отображаемые названия тарифов
PLAN_TITLES = {
    "start": "Старт",
    "standard": "Стандарт",
    "pro": "Профи",
}

# --- Пробный период ---
# Сколько бесплатных генераций выдать новому пользователю
FREE_GEN_TRIAL = int(os.getenv("FREE_GEN_TRIAL", "5"))
