from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from ..models.plan import SubscriptionPlanRead

def plans_list_keyboard(
    plans: list[SubscriptionPlanRead]
) -> InlineKeyboardMarkup:
    keyboard = []

    for plan in plans:
        keyboard.append([
            InlineKeyboardButton(
                f"{plan.title} · {plan.amount_usd}$",
                callback_data=f"plan:{plan.id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(keyboard)

def plan_info_keyboard(
    plan_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Выбрать способ оплаты", callback_data=f"plan:{plan_id}:pay")],
        [InlineKeyboardButton("Назад", callback_data="plan:list")]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_methods_keyboard(
    plan_id: int,
    payment_methods: list
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=payment_method.title,
                callback_data=f"plan:{plan_id}:pay:{payment_method.id}"
            )
        ]
        for payment_method in payment_methods
    ]
    keyboard.append([
        InlineKeyboardButton("Назад", callback_data=f"plan:{plan_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)

# ------------ Admin keyboards ------------

def plans_edit_keyboard(
    plans: list[SubscriptionPlanRead]
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                f"{plan.title} · {plan.amount_usd}$",
                callback_data=f"plan:patch:{plan.id}"
            )
        ]
        for plan in plans
    ]
    keyboard.insert(0, [InlineKeyboardButton("Создать", callback_data="plan:create")])
    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(keyboard)

def plan_create_exit() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text="Отмена",
            callback_data=f"plan:create:exit"
        )
    ]]
    return InlineKeyboardMarkup(keyboard)

def plan_create_confirm() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"plan:create:confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="Выйти",
                callback_data=f"plan:create:exit"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def plan_patch_exit() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text="Отмена",
            callback_data=f"plan:patch:exit"
        )
    ]]
    return InlineKeyboardMarkup(keyboard)

def plan_patch_confirm() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"plan:patch:confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="Выйти",
                callback_data=f"plan:patch:exit"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)