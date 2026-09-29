from telegram import Update
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

    plans: list[SubscriptionPlanRead] = context.bot_data["plans"]

    text = "Доступные подписки:\n\n"

    for plan in plans:
        amount_kgs = round(87 * plan.amount_usd, 2)
        amount_rub = round(85 * plan.amount_usd, 2)
        text += (
            f"• {plan.title} — "
            f"Стоимость: ~{amount_kgs} сом ({plan.amount_usd}$ / {amount_rub}₽)\n"
            f"{plan.description}\n\n"
        )

    await query.edit_message_text(
        text=text,
        reply_markup=plans_keyboard(plans)
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
        f"{plan.title}\n\n"
        f"{plan.description}\n\n"
        f"Стоимость: ~{amount_kgs} сом ({plan.amount_usd}$ / {amount_rub}₽)\n"
        f"Срок: {plan.duration_hours} ч."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=plan_keyboard(plan.id),
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
    
    context.bot_data["plans"] = plans
    plans: list[SubscriptionPlanRead] = context.bot_data["plans"]

    await query.edit_message_text(
        "Действие:",
        reply_markup=plans_edit_keyboard(plans)
    )