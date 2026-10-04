from telegram.ext import Application

from ..models.lava import InvoiceSchema

async def handle_payment_result(
    app: Application,
    telegram_id: int,
    payload: dict
):
    invoice: InvoiceSchema = app.bot_data["invoices"][telegram_id]
    invoice.status = payload["status"]

    event_status = payload["event_status"]
    subscription_id = payload["subscription_id"]
    subscription_range = payload["subscription_range"]

    user = app.bot_data["users"][telegram_id]

    if event_status == "success":
        user["subscription"] = {
            "id": subscription_id,
            "started_at": subscription_range["started_at"],
            "expires_at": subscription_range["expires_at"]
        }

    elif event_status == "failed":
        user_sub = user.get("subscription")
        if user_sub is None:
            return
        if user_sub.get("id") == subscription_id:   
            user["subscription"]["expires_at"] = None