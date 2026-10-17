import logging

from typing import Literal

from telegram.ext import Application
from telegram.error import TelegramError
from telegram.constants import ParseMode

from ..keyboards.menu_keyboard import back_to_menu_keyboard

logger = logging.getLogger("services.notifications")

def _invoice_completed_text() -> str:
    return (f"✅ <b>Успешная оплата!</b>")

def _invoice_failed_text() -> str:
    return (f"⛔️ <b>Ошибка платежа</b>\n\n"
            f"<i>❗️Попробуйте еще раз позднее</i>")

def _invoice_cancelled_text() -> str:
    return (f"⛔️ <b>Платеж был отменен</b>\n\n"
            f"<i>❗️Если вы не отменяли платеж, попробуйте еще раз позднее</i>")

MESSAGES_TEMPLATE = {
    "failed": _invoice_failed_text,
    "cancelled": _invoice_cancelled_text,
    "completed": _invoice_completed_text
}

def _notification_text(reason: str, custom_text: str | None = None) -> str | None:
    if custom_text is None:
        template = MESSAGES_TEMPLATE.get(reason)
        if template is not None:
            return template()
        return template
    return custom_text

async def send_notification_to_user(
    application: Application,
    telegram_id: int,
    reason: Literal["completed", "failed", "cancelled"],
    custom_text: str | None = None,
) -> None:
    text = _notification_text(reason, custom_text)    
    if text is None:
        logger.warning("Message text not found. `reason`: %s",
                       reason)
        return

    message_id: int = application.bot_data["payment_messages"].get(telegram_id)
    reply_markup = application.bot_data["payment_keyboard"].get(telegram_id)
    try:
        try:
            if custom_text is None:
                await application.bot.edit_message_text(
                    chat_id=telegram_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=back_to_menu_keyboard(),
                    parse_mode=ParseMode.HTML
                )
            else:
                await application.bot.edit_message_text(
                    chat_id=telegram_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )

        except AttributeError:
            await application.bot.send_message(
                chat_id=telegram_id,
                text=text,
                reply_markup=back_to_menu_keyboard(),
                parse_mode=ParseMode.HTML
            )

        logger.info("Notification sended. User: %s. Reason: %s",
                    telegram_id,
                    reason)
    
    except TelegramError as exc:
        logger.error("Failed send notification to user: %s | %s",
                     telegram_id,
                     exc.message)

    except Exception as exc:
        logger.exception("Unexpected exception: %s",
                         str(exc),
                         exc_info=True)