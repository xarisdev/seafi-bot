from ...client.models.api import Plan, Subscription

def subscription_info(
    plan: Plan,
    subscription: Subscription
) -> str:
    if subscription.expires_at is None:
        return ""
    
    expires_at = subscription.expires_at.isoformat().split("T")[0]
    
    text = (
        f"<b>Ваш план:</b> {plan.title}\n"
        f"Id: {subscription.id}:{subscription.user_id}\n\n"

        f"<b>Продолжительность:</b> {plan.duration // 24} д.\n"
        f"<b>Заканчивается:</b> {expires_at}\n\n"
    )
    return text