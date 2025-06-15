from aiogram import types
from keyboards import get_main_keyboard
from utils.user_state import set_user_state, STATE_MENU
from utils.user_roles import set_user_role, get_user_role, ROLE_LIMITS

ROLE_ORDER = ["user_free", "user_basic", "user_pro", "admin"]
SETROLE_PASSWORD = "qweqweqwe"

async def start(message: types.Message):
    user_id = message.from_user.id
    set_user_state(user_id, STATE_MENU)
    await message.answer(
        "👋 Привет! Я помогу сгенерировать логотип. Выбери действие:",
        reply_markup=get_main_keyboard()
    )

async def setrole_command(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.strip().split()

    if len(parts) != 4 or parts[0] != "/setrole" or parts[1] != "me":
        await message.answer(
            "❓ Формат команды:\n"
            "<code>/setrole me ПАРОЛЬ user_basic</code>\n"
            "<code>/setrole me ПАРОЛЬ up</code>\n"
            "<code>/setrole me ПАРОЛЬ down</code>",
            reply_markup=get_main_keyboard()
        )
        return

    _, _, password, action = parts

    if password != SETROLE_PASSWORD:
        await message.answer("❌ Неверный пароль.", reply_markup=get_main_keyboard())
        return

    current_role = get_user_role(user_id)
    current_index = ROLE_ORDER.index(current_role)

    if action == "up":
        new_index = min(current_index + 1, len(ROLE_ORDER) - 1)
        new_role = ROLE_ORDER[new_index]
    elif action == "down":
        new_index = max(current_index - 1, 0)
        new_role = ROLE_ORDER[new_index]
    elif action in ROLE_ORDER:
        new_role = action
    else:
        await message.answer(
            "❌ Неверная роль. Допустимые значения: user_free, user_basic, user_pro, admin, up, down.",
            reply_markup=get_main_keyboard()
        )
        return

    set_user_role(user_id, new_role)
    await message.answer(
        f"✅ Ваша роль обновлена: <b>{new_role}</b>\n"
        f"🔁 Лимиты генераций и векторизаций были обнулены.",
        reply_markup=get_main_keyboard()
    )
