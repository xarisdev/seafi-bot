from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Выбор подписки", callback_data="plan:list")
        ],
        [
            InlineKeyboardButton("Настроить фильтр", callback_data="search:edit")
        ],
        [
            InlineKeyboardButton("Профиль", callback_data="user:view"),
            InlineKeyboardButton("О боте", callback_data="bot:info")
        ]
    ]
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("Настроить тарифы", callback_data="plan:setup")
        ])
    
    return InlineKeyboardMarkup(keyboard)