import logging

from telegram import Update, CallbackQuery
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.plan_keyboard import (
    plans_list_keyboard,
    selected_plan_keyboard,
    plans_edit_keyboard,
    payment_methods_keyboard
)
from ..keyboards.payment_keyboard import selected_payment_keyboard, cancel_old_invoice_keyboard

from ..client.api_client import api_client
from ..client.models.exceptions import APIException, NotFoundError, BadRequestError
from ..client.models.api import Plan

logger = logging.getLogger("handlers.plans")

# ------------ Utils ------------

def plan_formatting(title: str, amount: float) -> str:
    amount_kgs = int(amount * 87)
    text = (
        f"<b>{title}</b>\n"
        f"{amount}$ · ~{amount_kgs} сом\n\n"
    )
    return text

def plan_info_formatting(plan: Plan) -> str:
    amount_kgs = int(87 * plan.amount)
    amount_rub = int(85 * plan.amount)

    text = (
        f'<b>План:</b> "{plan.title}"\n\n'
        f'{plan.description}\n\n'
        f'<b>💲{plan.amount}$ · ~{amount_kgs} сом · ~{amount_rub} ₽</b>\n'
        f'<b>⏱ {plan.duration//24} д.</b>'
    )
    return text

def to_pay_text(amount_usd: float, currency: str) -> str:
    sign = "$"
    exchange_rate = 1
    if currency == "RUB":
        sign = "₽"
        exchange_rate = 85

    final_amount = round(amount_usd * exchange_rate, 2)
    
    text = f"<b>К оплате:</b> {final_amount} {sign}"
    return text

async def get_selected_plan(
    query: CallbackQuery,
    plan_id: int,
    bot_data: dict,
) -> Plan | None:
    plans: dict[int, Plan] = bot_data.get("plans", {})
    plans_list = [plan for plan in plans.values()]

    selected_plan = plans.get(plan_id)
    if selected_plan is None:
        await query.edit_message_text(
            "Этот план больше не доступен",
            reply_markup=plans_list_keyboard(plans_list)
        )
        return None
    
    return selected_plan

# ------------ Handlers ------------

# "Выбрать план" / "plans:list"
async def plans_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plans = context.bot_data.get("plans", {})
    plans_list: list[Plan] = [plan for plan in plans.values()]

    text = (
        "✨Свежие объявления о недвижимости — без ручного поиска\n\n"
        "<b>▼// Доступные планы:</b>\n\n"
    )

    for plan in plans_list:
        text += plan_formatting(
            title=plan.title,
            amount=plan.amount
        )

    await query.edit_message_text(
        text=text,
        reply_markup=plans_list_keyboard(plans_list),
        parse_mode=ParseMode.HTML
    )

# "Выбранный план" / "plans:{id}"
async def selected_plan_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.split(":")[1])

    selected_plan = await get_selected_plan(
        query=query,
        plan_id=plan_id,
        bot_data=context.bot_data
    )
    if selected_plan is None:
        return

    text = plan_info_formatting(selected_plan)

    await query.edit_message_text(
        text=text,
        reply_markup=selected_plan_keyboard(selected_plan.id),
        parse_mode=ParseMode.HTML
    )

# "Выбрать способ оплаты" / "plans:{id}:pay"
async def select_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.split(":")[1])

    selected_plan = await get_selected_plan(
        query=query,
        plan_id=plan_id,
        bot_data=context.bot_data
    )
    if selected_plan is None:
        return
    #                                                                to future: need api
    keyboard = payment_methods_keyboard(
        plan_id,
        [
            "🌎 VISA / MasterCard",
            "🇷🇺 МИР / СБП (+8%)"
        ],
        [
            "USD",
            "RUB"
        ]
    )

    await query.edit_message_reply_markup(reply_markup=keyboard)

# "Выбранный способ оплаты" / "plans:{id}:pay:{currency}"
#                                                                    to future: currency -> method_id
async def selected_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    plan_id = int(data[1])
    currency = data[3]

    telegram_id = update.effective_user.id

    async with context.bot_data["locks"][telegram_id]:
        selected_plan = await get_selected_plan(
            query=query,
            plan_id=plan_id,
            bot_data=context.bot_data
        )
        if selected_plan is None:
            return

        try:
            invoice = await api_client.create_invoice(
                plan_id=selected_plan.id,
                currency=currency,
                telegram_id=telegram_id
            )
        except BadRequestError:
            await query.edit_message_text(
                "У вас осталась незавершенная оплата.\n\nНажмите ниже чтобы отменить:",
                reply_markup=cancel_old_invoice_keyboard()
            )
            return
        
        except APIException as e:
            logger.error("Create invoice error")
            await query.edit_message_text("Ошибка связи с сервером, попробуйте позднее")
            return

        keyboard = selected_payment_keyboard(payment_url=invoice.payment_url)

        context.bot_data["pending_invoices"][telegram_id] = invoice
        context.bot_data["payment_messages"][telegram_id] = query.message.message_id
        context.bot_data["payment_keyboard"][telegram_id] = keyboard

    text = (
        f"<b>Ссылка на оплату - {selected_plan.title}</b>\n\n"
        f"{to_pay_text(selected_plan.amount, currency)}\n\n"
        f"<b>Важно: </b>"
        f"<i>Ссылка действительная в течение 15 минут</i>"
    )
    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

# ------------ Admins ------------

# "Настроить тарифы" / "plans:setup"
async def plans_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_data = context.bot_data
    telegram_id = update.effective_user.id

    async with bot_data["locks"][telegram_id]:
        try:
            plans = await api_client.get_plans()
            for plan in plans:
                bot_data["plans"][plan.id] = plan
        
        except NotFoundError:
            plans = []
        
        except APIException:
            await query.edit_message_text(
                f"Сервер вернул ошибку:",
                reply_markup=plans_list_keyboard(plans)
            )
            return

    await query.edit_message_text(
        "Выберите действие:",
        reply_markup=plans_edit_keyboard(plans)
    )

plans_list_handler = CallbackQueryHandler(
    plans_list,
    pattern=r"^plans:list$"
)
plans_setup_handler = CallbackQueryHandler(
    plans_setup,
    pattern=r"^plans:setup$"
)
selected_plan_info_handler = CallbackQueryHandler(
    selected_plan_info,
    pattern=r"^plans:\d+$"
)
select_payment_methods_handler = CallbackQueryHandler(
    select_payment_methods,
    pattern=r"^plans:(\d+):pay$"
)
selected_payment_method_handler = CallbackQueryHandler(
    selected_payment_method,
    pattern=r"^plans:(\d+):pay:(.{3})$"
)