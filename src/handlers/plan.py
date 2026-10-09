from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.plan import (
    plan_info_keyboard,
    plans_list_keyboard,
    plans_edit_keyboard,
    payment_methods_keyboard
)
from ..keyboards.payment import (
    payment_keyboard
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
        
        amount_kgs = int(87 * plan.amount_usd)
        text += (
            f"<b>{plan.title}</b>\n"
            f"💲{plan.amount_usd}$ · ~{amount_kgs} сом\n\n"
        )

    await query.edit_message_text(
        text=text,
        reply_markup=plans_list_keyboard(plans_list),
        parse_mode=ParseMode.HTML
    )

async def selected_plan_info(
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

    amount_kgs = int(87 * selected_plan.amount_usd)
    amount_rub = int(85 * selected_plan.amount_usd)

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

async def plan_payment_methods(
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

    keyboard = payment_methods_keyboard(
        plan_id,
        [
            "🌎 VISA / MasterCard",
            "🇷🇺 МИР / СБП (+8%)"
        ],
        ["USD", "RUB"]
    )

    await query.edit_message_reply_markup(reply_markup=keyboard)

async def selected_plan_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    _, plan_id, _, currency = query.data.split(":")

    bot_plans = context.bot_data.get("plans", {})
    selected_plan: SubscriptionPlanRead = bot_plans.get(int(plan_id))

    telegram_id = update.effective_user.id

    payment_data = await api_client.create_payment_link(
        plan_id=selected_plan.id,
        telegram_id=telegram_id,
        currency=currency
    )
    invoice = payment_data.invoice
    subscription = payment_data.subscription

    context.bot_data["invoices"][invoice.id] = invoice
    context.bot_data["user_subscriptions"][telegram_id] = subscription

    # --------------------------------------------------
    # TODO: refactor, safety . . .  --------------------
    _kf = {"RUB": 85, "USD": 1.00}.get(currency)
    amount = round(selected_plan.amount_usd * _kf, 2)
    sign = {"RUB": "₽", "USD": "$"}.get(currency)
    to_pay_text = f"<b>К оплате:</b> {amount} {sign}\n\n"
    # --------------------------------------------------

    payment_timeout_m = invoice.payment_timeout_s // 60
    text = (
        f"<b>Ссылка на оплату - {selected_plan.title}</b>\n\n"
        f"{to_pay_text}"
        f"<b>Важно: </b>"
        f"<i>Ссылка действительная в течение {payment_timeout_m} минут</i>"
    )
    await query.edit_message_text(
        text=text,
        reply_markup=payment_keyboard(invoice["paymentUrl"]),
        parse_mode=ParseMode.HTML
    )


plans_list_handler = CallbackQueryHandler(
    plans_list,
    pattern=r"^plan:list$"
)
plans_setup_handler = CallbackQueryHandler(
    plans_setup,
    pattern=r"^plan:setup$"
)
selected_plan_info_handler = CallbackQueryHandler(
    selected_plan_info,
    pattern=r"^plan:\d+$"
)
plan_payment_methods_handler = CallbackQueryHandler(
    plan_payment_methods,
    pattern=r"^plan:(\d+):pay$"
)
selected_plan_payment_handler = CallbackQueryHandler(
    selected_plan_payment,
    pattern=r"^plan:(\d+):pay:(.{3})$"
)