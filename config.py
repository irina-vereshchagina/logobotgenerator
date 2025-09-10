import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Приводим к булевому значению (true → True, все остальное → False)
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- TARIFS (Stars) ---
PLAN_PRICES = {
    "start": 500,     # Старт — 500⭐
    "standard": 1000, # Стандарт — 1000⭐
    "pro": 1500,      # Профи — 1500⭐
}

PLAN_QUOTAS = {
    "start":    {"gen": 10, "vec": 0},  # 10 генераций, без векторизации
    "standard": {"gen": 15, "vec": 1},  # 15 генераций, 1 векторизация
    "pro":      {"gen": 30, "vec": 3},  # 30 генераций, 3 векторизации
}

PLAN_TITLES = {
    "start": "Тариф Старт",
    "standard": "Тариф Стандарт",
    "pro": "Тариф Профи",
}

# --- FREE TRIAL ---
FREE_GEN_TRIAL = 5  # 5 бесплатных генераций для каждого нового пользователя
