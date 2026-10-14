from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from ..app.config import settings

def info_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Условия использования",
                url=f"{settings.BASE_SERVER_URL}/terms-of-service/"
            )
        ],
        [
            InlineKeyboardButton(
                text="Политика конфиденциальности",
                url=f"{settings.BASE_SERVER_URL}/privacy-policy/"
            )
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data="menu:main"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)