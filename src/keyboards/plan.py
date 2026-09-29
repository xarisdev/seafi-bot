from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from ..models.plan import SubscriptionPlanRead

def plans_keyboard(
        subscriptions: list[SubscriptionPlanRead]
) -> InlineKeyboardMarkup:
    keyboard = []

    for subscription in subscriptions:
        keyboard.append([
            InlineKeyboardButton(
                f"{subscription.title} - {subscription.amount}",
                callback_data=f"plan:{subscription.id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(keyboard)

def plan_keyboard(
    subscription_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Оплатить", callback_data=f"plan:{subscription_id}:pay")],
        [InlineKeyboardButton("Назад", callback_data="menu:main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_methods_keyboard(
    subscription_id: int,
    payment_methods: list
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=payment_method.title,
                callback_data=f"plan:{subscription_id}:pay:{payment_method.id}"
            )
        ]
        for payment_method in payment_methods
    ]
    keyboard.append([
        InlineKeyboardButton("Назад", callback_data=f"plan:{subscription_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)