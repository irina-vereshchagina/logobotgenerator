import requests
from io import BytesIO
import asyncio
import logging

from config import USE_PLACEHOLDER, OPENAI_API_KEY

def _ensure_api_key():
    if not OPENAI_API_KEY and not USE_PLACEHOLDER:
        raise RuntimeError("OPENAI_API_KEY is not set in .env")

async def generate_image(prompt: str) -> BytesIO:
    """Генерация изображения логотипа через OpenAI или заглушку."""
    if USE_PLACEHOLDER:
        # заглушка (случайное фото) для локальных тестов
        url = "https://picsum.photos/1024/1024"
        resp = requests.get(url)
        resp.raise_for_status()
        return BytesIO(resp.content)

    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("Модуль openai не установлен. Выполните: pip install openai") from e

    _ensure_api_key()
    client = OpenAI(api_key=OPENAI_API_KEY)

    style = (
        "Create a clean, vector-like logo. "
        "Flat, minimal, high contrast, centered composition. "
        "Avoid text unless explicitly requested."
    )
    try:
        # формируем промпт через GPT-4o
        chat = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты создаешь промпт для генерации логотипа через DALL·E 3."},
                {"role": "user", "content": prompt},
            ],
        )
        prompt_dalle = chat.choices[0].message.content.strip()

        # генерация изображения через DALL·E 3
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_dalle,
            n=1,
            size="1024x1024",
            quality="standard",
            style="vivid",
        )
        image_url = image_response.data[0].url
        img_data = requests.get(image_url)
        img_data.raise_for_status()
        return BytesIO(img_data.content)
    except Exception as e:
        logging.exception("Ошибка при обращении к OpenAI")
        raise
