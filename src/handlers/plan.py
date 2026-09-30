from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from ..keyboards.plan import (
    plan_keyboard,
    plans_keyboard,
    plans_edit_keyboard,
    payment_methods_keyboard
)

from ..models.plan import SubscriptionPlanRead
from ..models.exceptions import (
    NotFoundError, APIError
)

from ..services.api import api_client

async def plans_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
): 
    query = update.callback_query
    await query.answer()

    plans: dict[int, SubscriptionPlanRead] = context.bot_data["plans"]
    plans_list = [plan for plan in plans.values()]

    text = "Автопоиск новых объявлений по вашим фильтрам 🔎\n\n<b>Доступные подписки:</b>\n\n"

    for plan in plans_list:
        amount_kgs = round(87 * plan.amount_usd, 2)
        text += (
            f"<b>{plan.title}</b>\n"
            f"💲{plan.amount_usd}$ · ~{amount_kgs} сом\n\n"
        )

    await query.edit_message_text(
        text=text,
        reply_markup=plans_keyboard(plans_list),
        parse_mode=ParseMode.HTML
    )

async def plan_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.split(":")[1])
    plan: SubscriptionPlanRead = context.bot_data["plans"][plan_id]

    if plan is None:
        await query.edit_message_text(
            "Эта подписка больше не доступна."
        )
        return

    amount_kgs = round(87 * plan.amount_usd, 2)
    amount_rub = round(85 * plan.amount_usd, 2)
    text = (
        f"<b>{plan.title}</b>\n\n"
        f"{plan.description}\n\n"
        f"<b>💲{plan.amount_usd}$ · ~{amount_kgs} сом · ~{amount_rub} ₽</b>\n"
        f"<b>⏱ {plan.duration_hours//24} д.</b>"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=plan_keyboard(plan.id),
        parse_mode=ParseMode.HTML
    )

async def plans_setup(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    try:
        plans = await api_client.get_plans()    
    except NotFoundError:
        plans = []

    for plan in plans:
        context.bot_data["plans"][plan.id] = plan

    plans: dict[int, SubscriptionPlanRead] = context.bot_data["plans"]

    await query.edit_message_text(
        "Действие:",
        reply_markup=plans_edit_keyboard([plan for plan in plans.values()])
    )