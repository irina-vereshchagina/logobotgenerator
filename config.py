# config.py
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Опционально: мок-режим генерации (для локальных тестов без OpenAI)
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

# Тарифы и квоты — ЕДИНЫЙ источник
PLAN_PRICES = {
    "start": 500,
    "standard": 1000,
    "pro": 1500,
}

PLAN_QUOTAS = {
    "start":    {"gen": 10, "vec": 0},
    "standard": {"gen": 15, "vec": 1},
    "pro":      {"gen": 30, "vec": 3},
}

# Сколько бесплатных генераций выдаём новому пользователю
FREE_GEN_TRIAL = 5
