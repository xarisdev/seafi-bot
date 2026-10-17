import logging

from datetime import datetime, timedelta

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.menu_keyboard import back_to_menu_keyboard
from ..keyboards.plan_keyboard import selected_plan_keyboard

from ..client.api_client import api_client
from ..client.models.exceptions import APIException

from ..services.payment_handler import check_payment_at_user

logger = logging.getLogger("handlers.payment")

# ------------ Utils ------------

def timeout(now: datetime, last_check: datetime | None) -> timedelta | None:
    if last_check is None:
        return None

    difference = now - last_check
    if difference < timedelta(seconds=5):
        return difference.total_seconds()
    
    return None

# ------------ Handlers ------------

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_data = context.bot_data
    telegram_id = update.effective_user.id

    last_check = context.user_data.get("last_check")

    async with bot_data["locks"][telegram_id]:
        context.user_data["last_check"] = datetime.now()

        diff = timeout(context.user_data["last_check"], last_check)

        if diff is not None:
            await query.edit_message_text(
                f"Подождите {diff} секунд",
                reply_markup=context.bot_data["payment_keyboard"].get(telegram_id)
            )
            return
        
        await check_payment_at_user(
            application=context,
            telegram_id=telegram_id,
            message_id=query.message.message_id
        )
    
async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_data = context.bot_data
    telegram_id = update.effective_user.id

    await query.edit_message_text(
        "⚠️ Отмена платежа...",
        reply_markup=None
    )
    async with bot_data["locks"][telegram_id]:
        try:
            local_invoice = bot_data["pending_invoices"].get(telegram_id)
            if local_invoice is None:
                invoices = await api_client.get_user_invoices(
                    telegram_id=telegram_id,
                    status="pending"
                )
                if len(invoices) < 1:
                    logger.warning("User %s has not pending invoices. Cancelled: 0")
                    await query.edit_message_text(
                        "Ожидающие платежи не найдены",
                        reply_markup=back_to_menu_keyboard()
                    )
                    return

                if len(invoices) > 1:
                    logger.warning("User %s has too many pending invoices. Cancelled: 1",
                                   telegram_id)

                local_invoice = invoices[0]

            await api_client.cancel_invoice(local_invoice.id)
        
        except APIException:
            await query.edit_message_text(
                "Ошибка связи с сервером, попробуйте позднее"
            )
            return

    await query.edit_message_text(
        "<b>Платеж успешно отменен!</b>",
        reply_markup=back_to_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )

payment_check_handler = CallbackQueryHandler(
    check_payment,
    pattern=r"^payment:check$"
)

payment_cancel_handler = CallbackQueryHandler(
    cancel_payment,
    pattern=r"^payment:cancel$"
)