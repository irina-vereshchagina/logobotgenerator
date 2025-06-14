import asyncio
from contextlib import asynccontextmanager

user_locks = {}
user_generation_flags = {}

@asynccontextmanager
async def single_user_lock(user_id: int):
    lock = user_locks.setdefault(user_id, asyncio.Lock())
    async with lock:
        yield

def is_generating(user_id):
    return user_generation_flags.get(user_id, False)

def set_generating(user_id, value: bool):
    user_generation_flags[user_id] = value
