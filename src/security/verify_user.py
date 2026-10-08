import logging

from telegram import Update
from telegram.ext import ContextTypes, ApplicationHandlerStop, TypeHandler
from telegram.error import TelegramError

from ..services.api import api_client
from ..models.exceptions import APIError, NotFoundError

logger = logging.getLogger("security.verify_user")

async def notify_msg(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    message_id: int,
    text: str
) -> None:
    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except TelegramError:
        pass
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )
    except TelegramError as e:
        logger.warning("Failed to notify chat %s: %s", chat_id, e)

async def reject_banned(update, context, flags) -> None:
    chat_id = update.effective_chat.id
    telegram_id = update.effective_user.id
    
    if flags:
        if flags.get("is_banned") is False:
            return
    else:
        try:
            return # TODO
            #if not await api_client.is_user_banned(telegram_id):
            #    return
        
        except NotFoundError:
            return
        
        except APIError as e:
            logger.warning(
                "APIError: %s | %s | %s", e.status_code, e.message, e.args,
                exc_info=True
            )
            await notify_msg(
                context=context,
                chat_id=chat_id,
                message_id=None,
                text="Ошибка сервиса. Попробуйте позднее."
            )
            raise ApplicationHandlerStop
        
    context.bot_data["user_flags"][telegram_id] = {
        "is_owner": False,
        "is_admin": False,
        "is_banned": True
    }
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Вы заблокированы."
        )
    except TelegramError as e:
        logger.warning("Failed to notify banned user %s: %s", telegram_id, e)

    raise ApplicationHandlerStop

async def verify_user_exists(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if update.effective_user is None or update.effective_message is None:
        raise ApplicationHandlerStop
    
    bot_data = context.bot_data

    telegram_id = update.effective_user.id

    chat_id = update.effective_chat.id
    message_id = update.effective_message.message_id

    users: dict = bot_data["users"]
    user_flags: dict = bot_data["user_flags"]

    flags = user_flags.get(telegram_id)
    await reject_banned(update, context, flags)
    
    if telegram_id in users and telegram_id in user_flags:
        return

    async with bot_data["locks"][telegram_id]:
        user = users.get(telegram_id)

        if user is None:
            try:
                user = await api_client.get_user(telegram_id)
        
            except NotFoundError:
                await notify_msg(
                    context=context,
                    chat_id=chat_id,
                    message_id=message_id,
                    text="Сначала необходимо зарегистрироваться. /start"
                )
                raise ApplicationHandlerStop
        
            except APIError as e:
                logger.warning(
                    "APIError: %s | %s | %s", e.status_code, e.message, e.args,
                    exc_info=True
                )
                await notify_msg(
                    context=context,
                    chat_id=chat_id,
                    message_id=message_id,
                    text="Ошибка сервиса. Попробуйте позднее."
                )
                raise ApplicationHandlerStop

            users[telegram_id] = user

        if flags is None:
            is_banned = False
            #is_banned = await api_client.is_user_banned(telegram_id)
            
            user_flags[telegram_id] = {
                "is_owner": False,
                "is_admin": False,
                "is_banned": is_banned
            }

        if user_flags[telegram_id]["is_banned"]:
            await notify_msg(
                context=context,
                chat_id=chat_id,
                message_id=message_id,
                text="Вы заблокированы."
            )
            raise ApplicationHandlerStop

verify_handler = TypeHandler(Update, verify_user_exists)