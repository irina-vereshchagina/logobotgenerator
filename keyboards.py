from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎨 Генерация логотипа")],
            [KeyboardButton(text="🖼 Векторизация")],
            [KeyboardButton(text="💎 Купить доступ")],   # ← добавили кнопку входа к оплате
            [KeyboardButton(text="ℹ️ Информация")],
        ],
        resize_keyboard=True
    )

def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True
    )
# Список тарифов для выбора
def get_plans_keyboard():
    # keyboards.py (добавь этот импорт в начало файла)
from config import PLAN_PRICES, PLAN_TITLES

    start = InlineKeyboardButton(
        text=f"Старт — {PLAN_PRICES['start']}⭐",
        callback_data="choose_plan:start"
    )
    standard = InlineKeyboardButton(
        text=f"Стандарт — {PLAN_PRICES['standard']}⭐",
        callback_data="choose_plan:standard"
    )
    pro = InlineKeyboardButton(
        text=f"Профи — {PLAN_PRICES['pro']}⭐",
        callback_data="choose_plan:pro"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [start],
        [standard],
        [pro],
    ])

# Кнопка "Оплатить N⭐" для выбранного тарифа
def get_pay_keyboard_for(plan_key: str, amount: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=f"Оплатить {amount}⭐",
                callback_data=f"pay_plan:{plan_key}"
            )
        ]]
    )
