import logging

from telegram.ext import Application
from telegram.error import TelegramError
from telegram.constants import ParseMode

from ..keyboards.menu_keyboard import back_to_menu_keyboard

logger = logging.getLogger("services.notifications")

async def send_payment_result(app: Application, telegram_id: int):
    message_id: int = app.bot_data["payment_msgs"].get(telegram_id)
    if message_id is None:
        return
    
    try:
        subscription = app.bot_data["user_subscriptions"][telegram_id]

        if subscription.status == "success":
            await app.bot.edit_message(
                chat_id=telegram_id,
                message_id=message_id,
                text=f'✅ <b>Успешная оплата!</b>\n\n',
                reply_markup=back_to_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )

        if subscription.status == "failed":
            await app.bot.edit_message(
                chat_id=telegram_id,
                message_id=message_id,
                text=f"⛔️ <b>Ошибка платежа / Отмена</b>\n\n",
                reply_markup=back_to_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )

        logger.info(
            "Notification | status: %s | user: %s",
            subscription.status,
            telegram_id
        )
    
    except TelegramError as exc:
        logger.warning(
            "Failed to send notification to user: %s | %s",
            telegram_id,
            exc.message
        )

    except Exception as exc:
        logger.exception("Unknown exception", exc_info=True)