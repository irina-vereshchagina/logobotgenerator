import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем логин и пароль из .env
user = os.getenv('VECTORIZE_USER')
password = os.getenv('VECTORIZE_PASS')

# Отправляем запрос
response = requests.post(
    'https://ru.vectorizer.ai/api/v1/vectorize',
    files={'image': open('image.jpg', 'rb')},
    data={'mode': 'test'},
    auth=(user, password)
)

# Обработка результата
if response.status_code == requests.codes.ok:
    with open('result.svg', 'wb') as out:
        out.write(response.content)
else:
    print("Error:", response.status_code, response.text)