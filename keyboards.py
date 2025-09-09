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

# Inline-кнопка, которая откроет окно оплаты Stars
def get_pay_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Оплатить 500⭐", callback_data="pay_500")
        ]]
    )
