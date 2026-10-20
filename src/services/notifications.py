import logging

from typing import Literal

from telegram import InlineKeyboardMarkup
from telegram.ext import Application
from telegram.error import TelegramError
from telegram.constants import ParseMode

from ..keyboards.menu_keyboard import back_to_menu_keyboard

from ..scripts.helpers.invoice_text import MESSAGES_TEMPLATE

logger = logging.getLogger("services.notifications")

async def send_message(
    application: Application,
    chat_id: int,
    text: str,
    reply_markup: InlineKeyboardMarkup | None
) -> bool:
    if reply_markup is None:
        reply_markup = back_to_menu_keyboard()
    try:
        await application.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return True
    
    except TelegramError as exc:
        logger.error("Failed send notification to user: %s | %s",
                     chat_id,
                     exc.message)

    except Exception as exc:
        logger.exception("Unexpected exception: %s",
                         str(exc),
                         exc_info=True)

    return False

async def edit_message(
    application: Application,
    chat_id: int,
    message_id: int,
    text: str | None,
    reply_markup: InlineKeyboardMarkup | None
) -> bool:    
    if reply_markup is None:
        reply_markup = back_to_menu_keyboard()
    try:
        await application.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return True

    except TelegramError as exc:
        logger.error("Failed send notification to user: %s | %s",
                     chat_id,
                     exc.message)

    except Exception as exc:
        logger.exception("Unexpected exception: %s",
                         str(exc),
                         exc_info=True)

    return False

async def notification_constructor(
    application: Application,
    chat_id: int,
    reason: str,
    update: bool = False,
    _is_payment_result: bool = False,
    _message_id: int = None,
    _custom_text: str = None,
    _custom_reply_markup: InlineKeyboardMarkup = None,
):
    logger.info("Construct notification..")

    # ------------ Validate ------------

    if _message_id is None and update is False:
        logger.warning("`_message_id` should be None if `update` is False")
    if update is True and _message_id is None:
        logger.warning("`_message_id` shouldn't be None if `update` is True")

    if _is_payment_result is True and _custom_text is not None:
        logger.warning("`_custom_text` should be None if `_is_payment_result` is True")
    if _is_payment_result is False and _custom_text is None:
        logger.error("`_custom_text` can't be None while `_is_payment_result` is None")
        return

    # ------------ Text setup ------------

    text = _custom_text
    if _is_payment_result:
        text = MESSAGES_TEMPLATE.get(reason)()
        
        if text is None:
            logger.error(
                "Unknown reason: %s",
                reason
            )
            return

    # ------------ Send ------------

    if not update or _message_id is None:
        result = await send_message(
            application=application,
            chat_id=chat_id,
            text=text,
            reply_markup=_custom_reply_markup
        )
    else:
        result = await edit_message(
            application=application,
            chat_id=chat_id,
            message_id=_message_id,
            text=text,
            reply_markup=_custom_reply_markup
        )

    if not result:
        logger.error("Notification failed. Data: %s",
                     [chat_id, reason, update, _is_payment_result, _message_id, _custom_text, _custom_reply_markup])
        return

    logger.info("Notification sended. User: %s. Reason: %s.",
                chat_id, reason)