import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")

# включает использование заглушек вместо OpenAI (для тестов)
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

# цены тарифов в звёздах
PLAN_PRICES = {
    "start": 500,
    "standard": 1000,
    "pro": 1500,
}

# квоты генераций/векторизаций для каждого тарифа
PLAN_QUOTAS = {
    "start": {"gen": 10, "vec": 0},
    "standard": {"gen": 15, "vec": 1},
    "pro": {"gen": 30, "vec": 3},
}

# бесплатные генерации для нового пользователя
FREE_GEN_TRIAL = 5
