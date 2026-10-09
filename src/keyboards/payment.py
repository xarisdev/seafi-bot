from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import KeyboardButtonStyle

def payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="⭐️ Оплатить",
                                 url=payment_url)
        ],
        [
            InlineKeyboardButton(text="🔄 Проверить",
                                 callback_data=f"payment:check")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена",
                                 callback_data="payment:cancel",
                                 style=KeyboardButtonStyle.DANGER)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)