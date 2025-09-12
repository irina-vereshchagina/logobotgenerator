# services/subscriptions.py
import json
import os
from typing import Dict, Any

from config import PLAN_QUOTAS, FREE_GEN_TRIAL

DB_FILE = "subscriptions.json"


def _load() -> Dict[str, Any]:
    """Загрузить базу подписок из файла"""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, Any]):
    """Сохранить базу подписок"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_quotas(user_id: int) -> Dict[str, int]:
    """Получить квоты пользователя. Если новый — выдать пробные генерации"""
    db = _load()
    uid = str(user_id)

    if uid not in db:
        db[uid] = {
            "plan": "free",
            "gen_left": FREE_GEN_TRIAL,
            "vec_left": 0,
        }
        _save(db)

    return db[uid]


def set_plan(user_id: int, plan: str):
    """Назначить тариф пользователю"""
    if plan not in PLAN_QUOTAS:
        raise ValueError(f"Неизвестный план: {plan}")

    db = _load()
    uid = str(user_id)
    quotas = PLAN_QUOTAS[plan]

    db[uid] = {
        "plan": plan,
        "gen_left": quotas.get("gen", 0),
        "vec_left": quotas.get("vec", 0),
    }
    _save(db)


def dec_gen(user_id: int) -> bool:
    """Списать одну генерацию. Возвращает True, если успешно"""
    db = _load()
    uid = str(user_id)
    if uid not in db:
        return False

    if db[uid]["gen_left"] > 0:
        db[uid]["gen_left"] -= 1
        _save(db)
        return True
    return False


def dec_vec(user_id: int) -> bool:
    """Списать одну векторизацию. Возвращает True, если успешно"""
    db = _load()
    uid = str(user_id)
    if uid not in db:
        return False

    if db[uid]["vec_left"] > 0:
        db[uid]["vec_left"] -= 1
        _save(db)
        return True
    return False
