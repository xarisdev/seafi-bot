from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🔹 Выбор тарифа 🔹", callback_data="plans:list")
        ],
        [
            InlineKeyboardButton("Настроить поиск 🔍", callback_data="search:edit")
        ],
        [
            InlineKeyboardButton("👤 Профиль", callback_data="user:view"),
            InlineKeyboardButton("🌐 О боте", callback_data="bot:info")
        ]
    ]
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("Настроить тарифы", callback_data="plans:setup")
        ])
    
    return InlineKeyboardMarkup(keyboard)

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton("◀️ Вернуться в меню", callback_data="menu:main")
    ]]
    return InlineKeyboardMarkup(keyboard)