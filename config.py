import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
