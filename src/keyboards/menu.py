from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def menu_keyboard(is_premium: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Выбор подписки", callback_data="sub:list")
        ],
        [
            InlineKeyboardButton("Профиль", callback_data="user:view"),
            InlineKeyboardButton("О боте", callback_data="bot:info")
        ]
    ]
    if is_premium:
        keyboard.insert(
            1,
            [InlineKeyboardButton("Настроить фильтр", callback_data="search:edit")]
        )
    
    return InlineKeyboardMarkup(keyboard)