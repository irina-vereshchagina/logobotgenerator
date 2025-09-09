import json
from pathlib import Path
from typing import Dict

_DB = Path("subscriptions.json")

def _load() -> Dict[str, dict]:
    if _DB.exists():
        return json.loads(_DB.read_text("utf-8"))
    return {}

def _save(data: Dict[str, dict]) -> None:
    _DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

def grant_plan(user_id: int, plan_key: str, gen: int, vec: int):
    data = _load()
    u = str(user_id)
    cur = data.get(u, {"gen_left": 0, "vec_left": 0, "history": []})
    cur["gen_left"] = int(cur.get("gen_left", 0)) + int(gen)
    cur["vec_left"] = int(cur.get("vec_left", 0)) + int(vec)
    cur["history"].append({"plan": plan_key, "gen": gen, "vec": vec})
    data[u] = cur
    _save(data)

def get_quotas(user_id: int) -> Dict[str, int]:
    data = _load()
    cur = data.get(str(user_id), {"gen_left": 0, "vec_left": 0})
    return {"gen_left": int(cur.get("gen_left", 0)), "vec_left": int(cur.get("vec_left", 0))}

def dec_gen(user_id: int) -> bool:
    data = _load()
    u = str(user_id)
    cur = data.get(u, {"gen_left": 0, "vec_left": 0})
    if cur.get("gen_left", 0) > 0:
        cur["gen_left"] -= 1
        data[u] = cur
        _save(data)
        return True
    return False

def dec_vec(user_id: int) -> bool:
    data = _load()
    u = str(user_id)
    cur = data.get(u, {"gen_left": 0, "vec_left": 0})
    if cur.get("vec_left", 0) > 0:
        cur["vec_left"] -= 1
        data[u] = cur
        _save(data)
        return True
    return False
