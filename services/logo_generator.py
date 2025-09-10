# services/logo_generator.py
import os
import io
import base64
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")


def _ensure_api_key():
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не задан в .env")


def _gen_sync_openai(prompt: str) -> io.BytesIO:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    style = (
        "Create a clean, vector-like logo. "
        "Flat, minimal, high contrast, centered composition. "
        "No background clutter."
    )

    resp = client.images.generate(
        model="gpt-image-1",
        prompt=f"{style}\nLogo idea: {prompt}",
        size=IMAGE_SIZE,
        background="transparent",
        n=1,
    )

    b64 = resp.data[0].b64_json
    return io.BytesIO(base64.b64decode(b64))


async def generate_image(prompt: str) -> io.BytesIO:
    """Асинхронная обёртка для генерации логотипа через OpenAI."""
    _ensure_api_key()
    return await asyncio.to_thread(_gen_sync_openai, prompt)
