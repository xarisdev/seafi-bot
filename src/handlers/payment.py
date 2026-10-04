from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.payment import (
    payment_keyboard
)

from ..models.plan import SubscriptionPlanRead
from ..models.lava import InvoiceSchema
from ..models.exceptions import (
    NotFoundError, APIError
)

from ..services.api import api_client

async def payment_selector(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    # temporary
    # _lava_payment_id = 1
    # ---------

    telegram_id = update.effective_user.id

    plan_id = int(query.data.split(":")[1])
    bot_plans = context.bot_data.get("plans", {})
    selected_plan: SubscriptionPlanRead = bot_plans.get(plan_id)

    invoice = await api_client.create_payment_link(
        plan_id=selected_plan.id,
        telegram_id=telegram_id
    )
    payment_timeout = invoice.payment_timeout_s * 60

    context.bot_data["invoices"][telegram_id] = invoice

    text = (
        f"<b>Ссылка на оплату - {selected_plan.title}</b>\n\n"
        f"<b>К оплате:</b> {selected_plan.amount_usd}$\n\n"
        f"<b>Важно:</b>"
        f"<i>Ссылка действительная в течение {payment_timeout} минут</i>"
    )
    await query.edit_message_text(
        text=text,
        reply_markup=payment_keyboard(invoice.paymentUrl),
        parse_mode=ParseMode.HTML
    )

async def check_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id

    invoice: InvoiceSchema = context.bot_data["payments"].get(telegram_id)
    if invoice is None:
        return

    # placeholder
    return
    
async def cancel_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    # placeholder
    return

payment_selector_handler = CallbackQueryHandler(
    payment_selector,
    pattern=r"^plan:(\d+):pay$"
)

payment_check_handler = CallbackQueryHandler(
    check_payment,
    pattern=r"^payment:check$"
)

payment_cancel_handler = CallbackQueryHandler(
    cancel_payment,
    pattern=r"^payment:cancel$"
)