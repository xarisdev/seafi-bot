from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards.subscription import (
    subscriptions_keyboard,
    subscription_keyboard,
    payment_methods_keyboard
)

from ..models.subscription import SubscriptionRead
from ..models.exceptions import (
    NotFoundError, APIError
)

from ..services.api import api_client

async def subscriptions_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
): 
    query = update.callback_query
    await query.answer()

    subscriptions: list[SubscriptionRead] = context.bot_data["subscriptions"]

    text = "Доступные подписки:\n\n"

    for subscription in subscriptions:
        amount_kgs = round(87 * subscription.amount_usd, 2)
        amount_rub = round(85 * subscription.amount_usd, 2)
        text += (
            f"• {subscription.title} — "
            f"Стоимость: ~{amount_kgs} сом ({subscription.amount_usd}$ / {amount_rub}₽)\n"
            f"{subscription.description}\n\n"
        )

    await query.edit_message_text(
        text=text,
        reply_markup=subscriptions_keyboard(subscriptions)
    )

async def subscription_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    subscription_id = int(query.data.split(":")[1])
    subscription: SubscriptionRead = context.bot_data["subscriptions"][subscription_id]

    if subscription is None:
        await query.edit_message_text(
            "Эта подписка больше не доступна."
        )
        return

    amount_kgs = round(87 * subscription.amount_usd, 2)
    amount_rub = round(85 * subscription.amount_usd, 2)
    text = (
        f"{subscription.title}\n\n"
        f"{subscription.description}\n\n"
        f"Стоимость: ~{amount_kgs} сом ({subscription.amount_usd}$ / {amount_rub}₽)\n"
        f"Срок: {subscription.duration_h} ч."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=subscription_keyboard(subscription.id),
    )