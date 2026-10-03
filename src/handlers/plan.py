from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.plan import (
    plan_info_keyboard,
    plans_list_keyboard,
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

    plans = context.bot_data.get("plans", {})
    plans_list = [plan for plan in plans.values()]

    text = (
        "Автопоиск новых объявлений по вашим фильтрам 🔎\n\n"
        "<b>Доступные подписки:</b>\n\n"
    )

    for plan in plans_list:
        plan: SubscriptionPlanRead
        
        amount_kgs = round(87 * plan.amount_usd, 2)
        text += (
            f"<b>{plan.title}</b>\n"
            f"💲{plan.amount_usd}$ · ~{amount_kgs} сом\n\n"
        )

    await query.edit_message_text(
        text=text,
        reply_markup=plans_list_keyboard(plans_list),
        parse_mode=ParseMode.HTML
    )

async def plan_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.split(":")[1])
    bot_plans = context.bot_data.get("plans", {})
    
    selected_plan: SubscriptionPlanRead = bot_plans.get(plan_id)

    if selected_plan is None:
        await query.edit_message_text(
            "Эта подписка больше не доступна",
            reply_markup=plans_list_keyboard(bot_plans)
        )
        return

    amount_kgs = round(87 * selected_plan.amount_usd, 2)
    amount_rub = round(85 * selected_plan.amount_usd, 2)

    text = (
        f"<b>{selected_plan.title}</b>\n\n"
        f"{selected_plan.description}\n\n"
        f"<b>💲{selected_plan.amount_usd}$ · ~{amount_kgs} сом · ~{amount_rub} ₽</b>\n"
        f"<b>⏱ {selected_plan.duration_hours//24} д.</b>"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=plan_info_keyboard(selected_plan.id),
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
    except APIError as err:
        await query.edit_message_text(
            f"Сетевая ошибка - {err}",
            reply_markup=plans_list_keyboard(plans)
        )

    for plan in plans:
        context.bot_data["plans"][plan.id] = plan

    plans: dict = context.bot_data.get("plans", {})

    await query.edit_message_text(
        "Выберите действие:",
        reply_markup=plans_edit_keyboard([
            plan for plan in plans.values()
        ])
    )

plans_list_handler = CallbackQueryHandler(
    plans_list,
    pattern=r"^plan:list$"
)
plans_setup_handler = CallbackQueryHandler(
    plans_setup,
    pattern=r"^plan:setup$"
)
plan_info_handler = CallbackQueryHandler(
    plan_info,
    pattern=r"^plan:\d+$"
)