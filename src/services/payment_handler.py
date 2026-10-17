import logging

from telegram.ext import Application

from ..client.api_client import api_client
from ..client.models.api import Invoice, WebSocketMessage
from ..client.models.exceptions import APIException, NotFoundError

from .notifications import send_notification_to_user

logger = logging.getLogger("services.payment_handler")

async def check_payment_at_wss(application: Application, message: WebSocketMessage):

    user_email_id = message.buyer_email.split("@")[0]
    user_telegram_id = int(user_email_id.split("_")[1])

    async with application.bot_data["locks"][user_telegram_id]:
        local_invoice: Invoice = application.bot_data["pending_invoices"].get(user_telegram_id)
        
        if local_invoice is None:
            logger.warning("Local invoice not found. telegram_id: %s",
                           user_telegram_id)
            return
        
        # Invoice validation
        if local_invoice.contract_id != message.contract_id:
            logger.warning(
                "Incorrect invoice [contract_id] received. Received: %s | Local: %s",
                message.contract_id,
                local_invoice.contract_id
            )
            return

        # Check status
        if message.invoice_status in ("failed", "cancelled"):
            await send_notification_to_user(
                application=application,
                telegram_id=user_telegram_id,
                reason=message.invoice_status
            )

        elif message.invoice_status == "completed":
            try:
                subscription = await api_client.get_active_subscription(telegram_id=user_telegram_id)

                if subscription is None:
                    await send_notification_to_user(
                        application=application,
                        telegram_id=user_telegram_id,
                        reason="error",
                        custom_text="Ошибка проверки подписки, попробуйте позднее. Если ошибка остается, напишите в поддержку." # TODO rtext
                    )
                    return
                
                else:
                    application.bot_data["subscriptions"][user_telegram_id] = subscription
                    await send_notification_to_user(
                        application=application,
                        telegram_id=user_telegram_id,
                        reason="completed"
                    )
            
            except APIException:
                await send_notification_to_user(
                    application=application,
                    telegram_id=user_telegram_id,
                    reason="error",
                    custom_text="Ошибка проверки подписки, попробуйте позднее. Если ошибка остается, напишите в поддержку." # TODO rtext
                )
                return

        else:
            logger.warning("Unexpected invoice status: %s | Webhook ID: %s",
                           message.invoice_status,
                           message.id)

        application.bot_data["payment_messages"].pop(user_telegram_id)
        application.bot_data["payment_keyboard"].pop(user_telegram_id)
        application.bot_data["pending_invoices"].pop(user_telegram_id)

async def check_payment_at_user(application: Application, telegram_id: int, message_id: int):

    application.bot_data["payment_messages"][telegram_id] = message_id
    local_invoice: Invoice = application.bot_data["pending_invoices"].get(telegram_id)

    if local_invoice is None:
        await send_notification_to_user(
            application=application,
            telegram_id=telegram_id,
            reason="error",
            custom_text="Ожидаемый платеж не найден. Если вы совершали платеж и видите это сообщение, обратитесь в поддержку."
        )
        return

    try:
        db_invoice = await api_client.check_invoice(invoice_id=local_invoice.id)
    
    except NotFoundError:
        logger.error("Invoice not found: %s",
                     local_invoice.id)

        await send_notification_to_user(
            application=application,
            telegram_id=telegram_id,
            reason="error",
            custom_text="Зарегистрированный платеж не найден. Если вы совершали платеж и видите это сообщение, обратитесь в поддержку."
        )
        return

    except APIException:
        await send_notification_to_user(
            application=application,
            telegram_id=telegram_id,
            reason="completed",
            custom_text="Ошибка проверки платежа, попробуйте позднее. Если ошибка остается, напишите в поддержку."
        )
        return

    if db_invoice.status == "pending":
        await send_notification_to_user(
            application=application,
            telegram_id=telegram_id,
            reason="pending",
            custom_text="<b>Статус платежа:</b> <i>Ожидание...</i>"
        )
        return

    if db_invoice.status in ("failed", "cancelled"):
        await send_notification_to_user(
            application=application,
            telegram_id=telegram_id,
            reason=db_invoice.status
        )

    elif db_invoice.status in "completed":
        try:
            subscription = await api_client.get_active_subscription(telegram_id)

            if subscription is None:
                await send_notification_to_user(
                    application=application,
                    telegram_id=telegram_id,
                    reason="error",
                    custom_text="Ошибка проверки подписки, попробуйте позднее. Если ошибка остается, напишите в поддержку." # TODO rtext
                )
                return
            
            else:
                application.bot_data["subscriptions"][telegram_id] = subscription
                await send_notification_to_user(
                    application=application,
                    telegram_id=telegram_id,
                    reason="completed"
                )

        except APIException:
            await send_notification_to_user(
                application=application,
                telegram_id=telegram_id,
                reason="error",
                custom_text="Ошибка проверки подписки, попробуйте позднее. Если ошибка остается, напишите в поддержку." # TODO rtext
            )
            return

    application.bot_data["payment_messages"].pop(telegram_id)
    application.bot_data["payment_keyboard"].pop(telegram_id)
    application.bot_data["pending_invoices"].pop(telegram_id)