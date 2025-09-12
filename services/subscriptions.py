import json
import os
from typing import Dict, Any
from config import PLAN_QUOTAS, FREE_GEN_TRIAL

DB_FILE = "subscriptions.json"

def _load() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(data: Dict[str, Any]) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def ensure_free_quota(user_id: int, free_gen: int = FREE_GEN_TRIAL, free_vec: int = 0) -> Dict[str, int]:
    """Выдать стартовые бесплатные квоты, если пользователя ещё нет в 'БД'."""
    data = _load()
    u = str(user_id)
    if u not in data:
        data[u] = {
            "plan": "free",
            "gen_left": int(free_gen),
            "vec_left": int(free_vec),
            "history": [{"plan": "free", "gen": int(free_gen), "vec": int(free_vec)}],
        }
        _save(data)
    cur = data[u]
    return {"gen_left": int(cur.get("gen_left", 0)), "vec_left": int(cur.get("vec_left", 0))}

def get_quotas(user_id: int) -> Dict[str, int]:
    data = _load()
    u = str(user_id)
    cur = data.get(u, {})
    return {"gen_left": int(cur.get("gen_left", 0)), "vec_left": int(cur.get("vec_left", 0))}

def set_plan(user_id: int, plan_key: str) -> None:
    """Назначить тариф пользователю."""
    if plan_key not in PLAN_QUOTAS:
        raise ValueError(f"Неизвестный план: {plan_key}")
    quotas = PLAN_QUOTAS[plan_key]
    data = _load()
    u = str(user_id)
    data[u] = {
        "plan": plan_key,
        "gen_left": int(quotas["gen"]),
        "vec_left": int(quotas["vec"]),
        "history": [{"plan": plan_key, "gen": int(quotas["gen"]), "vec": int(quotas["vec"])}],
    }
    _save(data)

def dec_gen(user_id: int) -> bool:
    """Списать одну генерацию."""
    data = _load()
    u = str(user_id)
    cur = data.get(u)
    if not cur:
        return False
    left = int(cur.get("gen_left", 0))
    if left <= 0:
        return False
    cur["gen_left"] = left - 1
    data[u] = cur
    _save(data)
    return True

def dec_vec(user_id: int) -> bool:
    """Списать одну векторизацию."""
    data = _load()
    u = str(user_id)
    cur = data.get(u)
    if not cur:
        return False
    left = int(cur.get("vec_left", 0))
    if left <= 0:
        return False
    cur["vec_left"] = left - 1
    data[u] = cur
    _save(data)
    return True
