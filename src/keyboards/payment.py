from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def payment_keyboard(
    payment_url: str
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Оплатить",
                url=payment_url
            )
        ],
        [
            InlineKeyboardButton(
                text="Проверить",
                callback_data=f"payment:check"
            )
        ],
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="payment:cancel"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)