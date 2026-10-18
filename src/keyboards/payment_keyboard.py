from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import KeyboardButtonStyle

def selected_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
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

def cancel_old_invoice_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Отменить",
                                 callback_data="payment:cancel",
                                 style=KeyboardButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton(text="🔄 Проверить",
                                 callback_data="payment:check")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)