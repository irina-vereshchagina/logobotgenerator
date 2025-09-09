# handlers/payments.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from config import STARS_PRICE, STARS_TITLE, STARS_DESC

router = Router(name=__name__)

# 👉 Нажали кнопку "Оплатить"
@router.callback_query(F.data == "pay_500")
async def on_pay_click(cq: CallbackQuery):
    prices = [LabeledPrice(label=STARS_TITLE, amount=STARS_PRICE)]  # сумма в ⭐
    payload = f"order:{cq.from_user.id}:{STARS_PRICE}"  # уникальный id заказа

    await cq.bot.send_invoice(
        chat_id=cq.message.chat.id,
        title=STARS_TITLE,
        description=STARS_DESC,
        payload=payload,
        currency="XTR",   # ⭐⭐ ВАЖНО: только XTR
        prices=prices,    # provider_token не нужен!
    )
    await cq.answer()

# 👉 Телеграм спрашивает "подтверждаешь оплату?"
@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    await q.bot.answer_pre_checkout_query(q.id, ok=True)

# 👉 Оплата прошла
@router.message(F.successful_payment)
async def on_success(m: Message):
    sp = m.successful_payment
    await m.answer(f"✅ Оплата прошла!\nПолучено: {sp.total_amount}⭐")
    # 🔑 здесь выдаёшь доступ / сохраняешь оплату в БД
