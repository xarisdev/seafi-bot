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
                callback_data=f"plans:{plan.id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(keyboard)

def selected_plan_keyboard(
    plan_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Выбрать способ оплаты (Lava)", callback_data=f"plans:{plan_id}:pay")],
        [InlineKeyboardButton("Назад", callback_data="plans:list")]
    ]
    return InlineKeyboardMarkup(keyboard)

def payment_methods_keyboard(
    plan_id: int,
    plan_title: list[str],
    payment_method_codes: list[str]
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=title,
                callback_data=f"plans:{plan_id}:pay:{code}"
            )
            for title, code in zip(plan_title, payment_method_codes)
        ]
    ]
    keyboard.append([
        InlineKeyboardButton("Назад", callback_data=f"plans:{plan_id}")
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
                callback_data=f"plans:patch:{plan.id}"
            )
        ]
        for plan in plans
    ]
    keyboard.insert(0, [InlineKeyboardButton("Создать", callback_data="plans:create")])
    keyboard.append([
        InlineKeyboardButton("Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(keyboard)

def plan_create_exit() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text="Отмена",
            callback_data=f"plans:create:exit"
        )
    ]]
    return InlineKeyboardMarkup(keyboard)

def plan_create_confirm() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"plans:create:confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="Выйти",
                callback_data=f"plans:create:exit"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def plan_patch_exit() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(
            text="Отмена",
            callback_data=f"plans:patch:exit"
        )
    ]]
    return InlineKeyboardMarkup(keyboard)

def plan_patch_confirm() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Подтвердить",
                callback_data=f"plans:patch:confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="Выйти",
                callback_data=f"plans:patch:exit"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)