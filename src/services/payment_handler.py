import logging

from telegram.ext import Application

from .web.api import api_client
from .web.exceptions import APIError, NotFoundError

from ..models.lava import InvoiceSchema
from ..models.websocket import Payload
from ..models.subscription import SubscriptionSchema

from .notifications import send_payment_result

logger = logging.getLogger(__name__)

async def _server_subscription(subscription_id: int) -> SubscriptionSchema:
    try:
        return await api_client.get_subscription(subscription_id=subscription_id)

    except NotFoundError:
        raise

    except APIError as e:
        logger.warning(
            "APIError: %s | %s | %s",
            e.status_code, e.message, e.args
        )
        raise

async def _server_active_subscription(telegram_id: int) -> SubscriptionSchema | None:
    try:
        # Либо подписка либо None
        return await api_client.get_active_subscription(telegram_id=telegram_id)
    
    except APIError as e:
        logger.warning(
            "APIError: %s | %s | %s",
            e.status_code, e.message, e.args
        )
        raise

async def ws_handle_payment_result(app: Application, payload: Payload):
    telegram_id = payload.telegram_id
    invoice_id = payload.invoice_id

    bot = app.bot_data

    async with bot["locks"][telegram_id]:
        invoice: InvoiceSchema = bot["invoices"].get(invoice_id)
        subscription: SubscriptionSchema = bot["user_subscriptions"].get(telegram_id)

        if invoice is None:
            logger.warning(
                "Local invoice not found. Payload: %s",
                payload.model_dump(mode='json')
            )
            return
        
        if invoice.status != "new":
            logger.warning(
                "SKIP | Local invoice status: %s",
                invoice.status
            )
            return

        if subscription is None:
            try:
                subscription = await _server_subscription(subscription_id=payload.subscription_id)
            
            except NotFoundError:
                logger.warning(
                    "Received subscription with id: %s not exists",
                    payload.subscription_id
                )
                return
            
            except APIError:
                return

            bot["user_subscriptions"][telegram_id] = subscription

        if payload.event_status == "success":
            await _activate_subscription(
                app=app,
                telegram_id=telegram_id,
                invoice=invoice,
                subscription=subscription,
                payload=payload
            )

        elif payload.event_status == "failed":
            await _delete_subscription(
                app=app,
                telegram_id=telegram_id,
                invoice=invoice,
                subscription=subscription,
                payload=payload
            )

        send_payment_result(app, telegram_id)

async def _activate_subscription(
    app: Application,
    telegram_id: int,
    invoice: InvoiceSchema,
    subscription: SubscriptionSchema,
    payload: Payload
):
    try: active_subscription = await _server_active_subscription(telegram_id=telegram_id)
    except APIError: return
    
    if active_subscription is None:
        try:
            db_subscription = await _server_subscription(subscription_id=payload.subscription_id)

            if db_subscription.status != "new":
                app.bot_data["user_subscriptions"][telegram_id] = db_subscription
                invoice.status = "success"

        except NotFoundError:
            invoice.status = "failed"
            subscription.status = "failed"
        
        except APIError:
            pass

        return

    app.bot_data["user_subscriptions"][telegram_id] = active_subscription
    invoice.status = payload.event_status

async def _delete_subscription(
    app: Application,
    telegram_id: int,
    invoice: InvoiceSchema,
    subscription: SubscriptionSchema,
    payload: Payload
):
    try: active_subscription = await _server_active_subscription(telegram_id=telegram_id)
    except APIError: return    
    # Ожидаемое поведение (неудачная оплата)
    if active_subscription is None:
        try:
            db_subscription = await _server_subscription(subscription_id=payload.subscription_id)
            app.bot_data["user_subscriptions"][telegram_id] = db_subscription
            if db_subscription.status != "new":
                invoice.status = "success"

        except NotFoundError:
            invoice.status = "failed"
            subscription.status = "failed"

        except APIError:
            pass
        
        return

    # Если внезапно после неудачно оплаты у сервера осталась другая активная подписка - подменяем, что внутри уже не особо важно
    app.bot_data["user_subscriptions"][telegram_id] = active_subscription
    invoice.status = "success"