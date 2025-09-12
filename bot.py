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

# --- Настройки квот ---
# Сколько бесплатных генераций выдать новому пользователю
FREE_GEN_TRIAL = int(os.getenv("FREE_GEN_TRIAL", "5"))

# Цены тарифов в Telegram Stars (или другой валюте, если поменяешь)
PLAN_PRICES = {
    "start": int(os.getenv("PRICE_START", "99")),
    "standard": int(os.getenv("PRICE_STANDARD", "249")),
    "pro": int(os.getenv("PRICE_PRO", "499")),
}

# Отображаемые названия тарифов
PLAN_TITLES = {
    "start": "Старт",
    "standard": "Стандарт",
    "pro": "Профи",
}

# Сколько квот выдаётся по каждому тарифу
PLAN_QUOTAS = {
    "start": {"gen": int(os.getenv("QUOTA_START_GEN", "20")), "vec": int(os.getenv("QUOTA_START_VEC", "2"))},
    "standard": {"gen": int(os.getenv("QUOTA_STANDARD_GEN", "60")), "vec": int(os.getenv("QUOTA_STANDARD_VEC", "6"))},
    "pro": {"gen": int(os.getenv("QUOTA_PRO_GEN", "150")), "vec": int(os.getenv("QUOTA_PRO_VEC", "20"))},
}
