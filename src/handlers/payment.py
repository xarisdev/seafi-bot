from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.menu import menu_keyboard
from ..keyboards.payment import (
    payment_keyboard
)

from ..models.plan import SubscriptionPlanRead
from ..models.lava import InvoiceSchema
from ..models.exceptions import (
    NotFoundError, APIError
)

from ..services.api import api_client

async def check_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id

    invoice: InvoiceSchema = context.bot_data["invoices"].get(telegram_id)
    if invoice is None:
        return

    payment_status = await api_client.check_payment(invoice)
    #placeholder
    return
    
async def cancel_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    is_admin = context.bot_data["users"][telegram_id].get("is_admin", False)

    invoice: InvoiceSchema = context.bot_data["invoices"].get(telegram_id)
    if invoice is None:
        await query.edit_message_text(
            "Отмена",
            reply_markup=menu_keyboard(is_admin)
        )
        return
    
    invoice.status = "cancel"

    await api_client.cancel_payment(telegram_id, invoice)

    await query.edit_message_text(
        "Оплата отменена",
        reply_markup=menu_keyboard(is_admin)
    )


payment_check_handler = CallbackQueryHandler(
    check_payment,
    pattern=r"^payment:check$"
)

payment_cancel_handler = CallbackQueryHandler(
    cancel_payment,
    pattern=r"^payment:cancel$"
)