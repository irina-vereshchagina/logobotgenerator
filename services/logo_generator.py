import requests
from io import BytesIO
import asyncio
from config import USE_PLACEHOLDER, OPENAI_API_KEY

async def generate_image(prompt: str) -> BytesIO:
    if USE_PLACEHOLDER:
        # await asyncio.sleep(0.)
        url = "https://placehold.co/1024x1024/png?text=Logo"
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    chat = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты создаешь промпт для генерации логотипа через DALL·E 3."},
            {"role": "user", "content": prompt}
        ]
    )

    prompt_dalle = chat.choices[0].message.content.strip()

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
