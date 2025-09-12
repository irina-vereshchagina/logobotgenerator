from aiogram import Router, types
from aiogram.types import BufferedInputFile
from keyboards import get_back_keyboard
from utils.user_state import single_user_lock, is_generating, set_generating, set_user_state, STATE_VECTORIZE
import logging
import os
import requests
from dotenv import load_dotenv

# 👇 добавили импорт квот
from services.subscriptions import get_quotas, dec_vec

# создаём роутер для этого модуля
router = Router()

load_dotenv()

VECTORIZE_USER = os.getenv("VECTORIZE_USER")
VECTORIZE_PASS = os.getenv("VECTORIZE_PASS")
