# services/logo_generator.py
import os
import io
import base64
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")


def _ensure_api_key():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не задан в .env")


def _gen_sync_openai(prompt: str) -> io.BytesIO:
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("Модуль openai не установлен. Выполни: pip install openai") from e

    client = OpenAI(api_key=OPENAI_API_KEY)

    style = (
        "Create a clean, vector-like logo. "
        "Flat, minimal, high contrast, centered composition. "
        "Avoid text unless explicitly requested."
    )

    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=f"{style}\nLogo idea: {prompt}",
            size=IMAGE_SIZE,
            n=1,
        )
        b64 = resp.data[0].b64_json
        return io.BytesIO(base64.b64decode(b64))
    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI")
        raise


async def generate_image(prompt: str) -> io.BytesIO:
    """Асинхронная функция генерации логотипа через OpenAI"""
    _ensure_api_key()
    return await asyncio.to_thread(_gen_sync_openai, prompt)
