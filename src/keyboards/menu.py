from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def menu_keyboard() -> InlineKeyboardMarkup:
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
    
    return InlineKeyboardMarkup(keyboard)