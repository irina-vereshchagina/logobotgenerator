from aiogram import Router, F
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from config import PLAN_PRICES, PLAN_QUOTAS, PLAN_TITLES
from keyboards import get_pay_keyboard_for
from services.subscriptions import grant_plan, get_quotas

router = Router(name=__name__)

# 1) Выбор тарифа
@router.callback_query(F.data.startswith("choose_plan:"))
async def on_choose_plan(cq: CallbackQuery):
    plan_key = cq.data.split(":")[1]
    if plan_key not in PLAN_PRICES:
        await cq.answer("Неизвестный тариф", show_alert=True)
        return
    amount = PLAN_PRICES[plan_key]
    title = PLAN_TITLES[plan_key]
    await cq.message.edit_text(
        f"<b>{title}</b>\n"
        f"• Генераций логотипов: {PLAN_QUOTAS[plan_key]['gen']}\n"
        f"• Векторизаций: {PLAN_QUOTAS[plan_key]['vec']}\n\n"
        f"Цена: {amount}⭐\n\n"
        f"Нажми, чтобы оплатить:",
    )
    await cq.message.edit_reply_markup(reply_markup=get_pay_keyboard_for(plan_key, amount))
    await cq.answer()

# 2) Кнопка "Оплатить N⭐" → отправляем инвойс Stars
@router.callback_query(F.data.startswith("pay_plan:"))
async def on_pay_plan(cq: CallbackQuery):
    plan_key = cq.data.split(":")[1]
    if plan_key not in PLAN_PRICES:
        await cq.answer("Неизвестный тариф", show_alert=True)
        return
    amount = PLAN_PRICES[plan_key]
    title = PLAN_TITLES[plan_key]
    prices = [LabeledPrice(label=title, amount=amount)]
    payload = f"order:{cq.from_user.id}:{plan_key}:{amount}"
    await cq.bot.send_invoice(
        chat_id=cq.message.chat.id,
        title=title,
        description=f"Оплата тарифа {title} в Telegram Stars",
        payload=payload,
        currency="XTR",     # Stars
        prices=prices,      # provider_token не указываем
    )
    await cq.answer()

# 3) Pre-checkout — обязательно ok=True
@router.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    await q.bot.answer_pre_checkout_query(q.id, ok=True)

# 4) Успешная оплата — начисляем квоты
@router.message(F.successful_payment)
async def on_success(m: Message):
    sp = m.successful_payment
    # payload: order:<user_id>:<plan_key>:<amount>
    try:
        _, uid_str, plan_key, amount_str = sp.invoice_payload.split(":")
    except Exception:
        plan_key = None

    if not plan_key or plan_key not in PLAN_QUOTAS:
        await m.answer("✅ Оплата прошла, но тариф не распознан. Напишите в поддержку.")
        return

    gen = PLAN_QUOTAS[plan_key]["gen"]
    vec = PLAN_QUOTAS[plan_key]["vec"]

    grant_plan(m.from_user.id, plan_key, gen=gen, vec=vec)

    q = get_quotas(m.from_user.id)
    await m.answer(
        "✅ Оплата прошла!\n"
        f"Начислено по тарифу <b>{PLAN_TITLES[plan_key]}</b>:\n"
        f"• Генераций: +{gen}\n"
        f"• Векторизаций: +{vec}\n\n"
        f"Текущий баланс: {q['gen_left']} генераций, {q['vec_left']} векторизаций."
    )
