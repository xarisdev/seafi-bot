import logging

from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.menu_keyboard import back_to_menu_keyboard
from ..keyboards.plan_keyboard import selected_plan_keyboard

from ..models.lava import InvoiceSchema
from ..models.plan import SubscriptionPlanRead
from ..models.subscription import SubscriptionSchema

from ..services.web.api import api_client
from ..services.web.exceptions import APIError, NotFoundError, ConflictError

logger = logging.getLogger("handlers.payment")

# ------------ Utils ------------

def timeout(now: datetime, last_check: datetime | None) -> bool:
    if last_check is None:
        return False
    if now - last_check < 7:
        return True
    return False

def get_subscription(bot_data, telegram_id: int) -> SubscriptionSchema | None:
    subscription: SubscriptionSchema = bot_data["user_subscriptions"].get(telegram_id)
    return subscription

def get_invoice(bot_data, telegram_id: int) -> InvoiceSchema | None:
    subscription = get_subscription(bot_data, telegram_id)
    if subscription is None:
        return None

    invoice_id = subscription.invoice_id
    
    invoice = bot_data["invoices"].get(invoice_id)
    return invoice

def format_new_status(previous_text: str) -> str:
    _status = "<b>Статус:</b>"
    status_text = "Ожидает оплаты.."
    if status_text in previous_text:
        return previous_text
    previous_text += f"\n\n{_status} {status_text}"
    return previous_text

def subscription_success_text(
    plan: SubscriptionPlanRead,
    subscription: SubscriptionSchema
) -> str:    
    date = subscription.expires_at.isoformat().split(".")[0]
    expires_at = date.replace("T", " ")

    text = (
        f'✅ <b>Успешная оплата!</b>\n\n'
        f'План: "{plan.title}"'
        f'Действителен до: {expires_at}'
        # Инструкции как начать пользоваться и т.д. / мб в отдельном файле оставить
    )
    return text

def subscription_failed_text() -> str:
    text = (
        f"⛔️ <b>Ошибка платежа / Отмена</b>\n\n"
        f"<i>❗️Если вы не отменяли платеж, попробуйте еще раз позднее</i>"
    )
    return text

# ------------ Handlers ------------

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_data = context.bot_data
    telegram_id = update.effective_user.id

    async with bot_data["locks"][telegram_id]:

        now = datetime.now()
        last_check = context.user_data.get("last_check")
        if timeout(now, last_check):
            return
        context.user_data["last_check"] = now

        is_admin = bot_data["user_flags"][telegram_id]["is_admin"]
        
        local_invoice = get_invoice(bot_data, telegram_id)
        if local_invoice is None:
            await query.edit_message_text(
                (
                "Не удалось найти платеж, если вы совершали платеж и видите это сообщение, пожалуйста, обратитесь в поддежрку: @seafi_support"
                "\n\nЕсли вы не совершали платеж, игнорируйте это сообщение."
                ),
                reply_markup=back_to_menu_keyboard()
            )
            return

        try:
            subscription = await api_client.check_payment(invoice_id=local_invoice.id)
        
        except NotFoundError:
            await query.edit_message_text(
                "Подписка не найдена",
                reply_markup=back_to_menu_keyboard()
            )
            return

        except APIError:
            await query.edit_message_text(
                "Сервер временно недоступен, пожалуйста, попробуйте позднее"
            )
            return

        # Update data
        bot_data["user_subscriptions"][telegram_id] = subscription
        bot_data["invoices"][local_invoice.id] = None

        # Send result to user
        if subscription.status == "new":
            previous_text = query.message.text
            new_text = format_new_status(previous_text)
            await query.edit_message_text(new_text, parse_mode=ParseMode.HTML)
            return
        
        plan = bot_data["plans"][subscription.plan_id]

        if subscription.status == "success":
            await query.edit_message_text(
                text=subscription_success_text(plan, subscription),
                reply_markup=back_to_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )

        if subscription.status == "failed":
            await query.edit_message_text(
                text=subscription_failed_text(),
                reply_markup=selected_plan_keyboard(plan.id),
                parse_mode=ParseMode.HTML
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
        is_admin = bot_data["user_flags"][telegram_id]["is_admin"]

        local_invoice = get_invoice(bot_data, telegram_id)
        if local_invoice is None:
            await query.edit_message_text(
                (
                "Не удалось найти платеж, если вы совершали платеж и видите это сообщение, пожалуйста, обратитесь в поддежрку: @seafi_support"
                "\n\nЕсли вы не совершали платеж, игнорируйте это сообщение."
                ),
                reply_markup=back_to_menu_keyboard()
            )
            return

        try:
            #await api_client.cancel_payment(local_invoice.id)
            pass

        except ConflictError:
            await query.edit_message_text(
                "Подписка уже активирована, невозможно отменить!",
                reply_markup=back_to_menu_keyboard()
            )

        except APIError as err:
            logger.warning(
                "Cancel payment API error: %s | %s | %s",
                err.status_code,
                err.message,
                err.args
            )

        bot_data["invoices"][local_invoice.id] = None

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