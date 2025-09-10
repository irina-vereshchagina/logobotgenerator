import json
import os
from config import PLAN_QUOTAS, FREE_GEN_TRIAL

DB_FILE = "subscriptions.json"


def _load():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}


def _save(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# 👇 бесплатные квоты при первом запуске
def ensure_free_quota(user_id: int, free_gen: int = FREE_GEN_TRIAL, free_vec: int = 0):
    """
    Выдать стартовые бесплатные квоты, если пользователя ещё нет в БД.
    Возвращает текущие квоты пользователя.
    """
    data = _load()
    u = str(user_id)
    if u not in data:
        data[u] = {
            "gen_left": int(free_gen),
            "vec_left": int(free_vec),
            "history": [{"plan": "free_trial", "gen": int(free_gen), "vec": int(free_vec)}],
        }
        _save(data)
    cur = data[u]
    return {"gen_left": int(cur.get("gen_left", 0)), "vec_left": int(cur.get("vec_left", 0))}


# добавить тариф пользователю (после покупки)
def grant_plan(user_id: int, plan_key: str, gen: int, vec: int):
    data = _load()
    u = str(user_id)
    if u not in data:
        data[u] = {"gen_left": 0, "vec_left": 0, "history": []}
    data[u]["gen_left"] = int(data[u].get("gen_left", 0)) + int(gen)
    data[u]["vec_left"] = int(data[u].g_]()
