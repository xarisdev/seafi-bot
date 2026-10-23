import logging

from telegram.ext import Application

from ..client.api_client import api_client
from ..client.models.api import Invoice, EnumInvoiceStatus, WebSocketMessage
from ..client.models.exceptions import APIException, NotFoundError

from .notifications import notification_constructor

from ..scripts.helpers.sub_info import subscription_info

logger = logging.getLogger("services.payment_handler")

# ------------ Helpers ------------

async def _compare_invoice(telegram_id: int, contract_id: str, status: str) -> Invoice | None:
    try:
        db_invoices = await api_client.get_user_invoices(
            telegram_id=telegram_id,
            status=status
        )
    except APIException as exc:
        logger.error(str(exc.args))
        return None

    for db_invoice in db_invoices:
        if db_invoice.contract_id == contract_id:
            return db_invoice
    
    return None

async def _db_invoice(telegram_id: int, status: str) -> list[Invoice] | None:
    try:
        invoices = await api_client.get_user_invoices(
            telegram_id=telegram_id,
            status=status
        )
    except APIException as exc:
        logger.error(str(exc.args))
        return None

    return invoices

async def _check_invoice(invoice_id: int) -> Invoice | None:
    try:
        invoice = await api_client.check_invoice(invoice_id=invoice_id)
        return invoice
    
    except NotFoundError:
        logger.error("Invoice %s not found",
                     invoice_id)
    
    except APIException as exc:
        logger.error(str(exc.args))

    return None

async def _synch_subscription(application: Application, telegram_id: int):
    subscription = await api_client.get_active_subscription(
        telegram_id=telegram_id
    )

    if subscription is None:
        logger.warning(
            "Active subscription not found. User: %s",
            telegram_id
        )
        return

    plan = application.bot_data["plans"].get(subscription.plan_id)
    text = subscription_info(plan=plan, subscription=subscription)

    await notification_constructor(
        application=application,
        chat_id=telegram_id,
        reason='completed',
        _custom_text=text
    )
    
    application.bot_data["subscriptions"][telegram_id] = subscription

async def _compare_invoice_status(application, telegram_id: int, invoice_status: str):
    bot_data = application.bot_data

    _message_id = bot_data["payment_messages"].pop(telegram_id, None)
    _payment_keyboard = bot_data["payment_keyboard"].pop(telegram_id, None)

    if invoice_status == EnumInvoiceStatus.PENDING:
        await notification_constructor(
            application=application,
            chat_id=telegram_id,
            reason=EnumInvoiceStatus.PENDING.value,
            update=True,
            _is_payment_result=True,
            _message_id=_message_id,
            _custom_reply_markup=_payment_keyboard
        )
    
    elif invoice_status == EnumInvoiceStatus.FAILED:
        await notification_constructor(
            application=application,
            chat_id=telegram_id,
            reason=EnumInvoiceStatus.FAILED.value,
            update=True,
            _is_payment_result=True,
            _message_id=_message_id
        )
    
    elif invoice_status == EnumInvoiceStatus.CANCELLED:
        await notification_constructor(
            application=application,
            chat_id=telegram_id,
            reason=EnumInvoiceStatus.CANCELLED.value,
            update=True,
            _is_payment_result=True,
            _message_id=_message_id
        )
    
    elif invoice_status == EnumInvoiceStatus.COMPLETED:
        await notification_constructor(
            application=application,
            chat_id=telegram_id,
            reason=EnumInvoiceStatus.COMPLETED.value,
            update=True,
            _is_payment_result=True,
            _message_id=_message_id
        )

        await _synch_subscription(
            application=application,
            telegram_id=telegram_id
        )

    else:
        logger.error("Unknown invoice status: %s", invoice_status)

    bot_data["pending_invoices"].pop(telegram_id, None)

# ------------ Handlers ------------

async def check_payment_at_wss(application: Application, message: WebSocketMessage):

    user_email_id = message.buyer_email.split("@")[0]
    user_telegram_id = int(user_email_id.split("_")[1])

    bot_data = application.bot_data

    async with bot_data["locks"][user_telegram_id]:
        local_invoice: Invoice = bot_data["pending_invoices"].get(user_telegram_id)

        # ------------ Invoice synchronization ------------

        if local_invoice is None:
            logger.warning("Local invoice not found. User: %s",
                           user_telegram_id)

            _invoice = await _compare_invoice(
                telegram_id=user_telegram_id,
                contract_id=message.contract_id,
                status=message.invoice_status
            )

            if _invoice is None:
                logger.error("Unknown invoice recieved: %s | %s for user %s",
                             message.contract_id,
                             message.invoice_status,
                             user_telegram_id)
                return

            local_invoice = _invoice
            bot_data["pending_invoices"][user_telegram_id] = local_invoice

        # ------------ Final ------------

        await _compare_invoice_status(
            application=application,
            telegram_id=user_telegram_id,
            invoice_status=message.invoice_status
        )

async def check_payment_at_user(application: Application, telegram_id: int, message_id: int):
    # ntfy: Under lock

    actual_invoice = None
    local_invoice: Invoice = application.bot_data["pending_invoices"].get(telegram_id)

    if local_invoice is None:

        invoices = await _db_invoice(telegram_id=telegram_id, status=EnumInvoiceStatus.PENDING.value)
        
        if not invoices:
            await notification_constructor(
                application=application,
                chat_id=telegram_id,
                reason="manual update",
                update=True,
                _message_id=message_id,
                _custom_text=(
                    "<b>Ожидающий оплату счет не найден!</b>\n\n"
                    "Если вы совершали платеж и видите это сообщение, <b>пожалуйста, обратитесь в поддержку:</b> @seafi_support"
                )
            )
            return

        last_invoice = invoices[0]

        actual_invoice = await _check_invoice(last_invoice.id)

        if actual_invoice is None:
            await notification_constructor(
                application=application,
                chat_id=telegram_id,
                reason="manual update",
                update=True,
                _message_id=message_id,
                _custom_text=(
                    "<b>Ожидающий оплату счет не найден!</b>\n\n"
                    "Если вы совершали платеж и видите это сообщение, <b>пожалуйста, обратитесь в поддержку:</b> @seafi_support"
                )
            )
            return

    invoice = local_invoice or actual_invoice

    await _compare_invoice_status(
        application=application,
        telegram_id=telegram_id,
        invoice_status=invoice.status
    )