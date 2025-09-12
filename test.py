import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем логин и пароль из .env
user = os.getenv("VECTORIZE_USER")
password = os.getenv("VECTORIZE_PASS")

if not user or not password:
    raise RuntimeError("Не заданы VECTORIZE_USER и VECTORIZE_PASS в .env")

# Путь к файлу для векторизации
image_path = "image.jpg"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Файл для векторизации не найден: {image_path}")

try:
    with open(image_path, "rb") as img:
        response = requests.post(
            "https://ru.vectorizer.ai/api/v1/vectorize",
            files={"image": img},
            data={"mode": "test"},   # можно заменить "test" на "high" или "photo"
            auth=(user, password),
            timeout=60,
        )

    if response.status_code == requests.codes.ok:
        result_file = "result.svg"
        with open(result_file, "wb") as out:
            out.write(response.content)
        print(f"✅ Векторизация завершена, результат сохранён в {result_file}")
    else:
        print(f"❌ Ошибка {response.status_code}: {response.text}")

except Exception as e:
    print(f"⚠️ Произошла ошибка при запросе: {e}")
