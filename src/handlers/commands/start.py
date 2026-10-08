import logging

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, ApplicationHandlerStop
from telegram.error import TelegramError

from ...services.api import api_client
from ...models.exceptions import NotFoundError, APIError

from ...keyboards.menu import menu_keyboard

from ...security.verify_user import reject_banned

logger = logging.getLogger("handlers.commands.start")

async def safe_send(chat_id = None, update = None, context = None, **kwargs):
    try:
        if update:
            await update.message.reply_text(**kwargs)

        elif context:
            await context.bot.send_message(chat_id=chat_id, **kwargs,)

        else:
            return
    
    except TelegramError as e:
        logger.warning(
            "Failed to send menu to %s: %s",
            chat_id or update.effective_chat.id,
            e
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_data = context.bot_data
    
    telegram_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_admin = False

    async with bot_data["locks"][telegram_id]:
        user = bot_data["users"].get(telegram_id)
        user_flags = bot_data["user_flags"].get(telegram_id)
        
        await reject_banned(update, context, user_flags)
        if user_flags:
            is_admin = user_flags["is_admin"]

        if user:
            await safe_send(
                chat_id=chat_id,
                context=context,
                text="Выберите действие:",
                reply_markup=menu_keyboard(is_admin)
            )
            raise ApplicationHandlerStop

        try:
            db_user = await api_client.get_user(telegram_id)

        except NotFoundError:
            try:
                db_user = await api_client.create_user(telegram_id)
            except APIError as e:
                logger.warning(
                    "APIError: %s | %s | %s", e.status_code, e.message, e.args,
                    exc_info=True
                )
                await safe_send(
                    chat_id=chat_id,
                    context=context,
                    text="Сервер временно недоступен, повторите попытку позднее."
                )
                raise ApplicationHandlerStop

        except APIError as e:
            logger.warning(
                "APIError: %s | %s | %s", e.status_code, e.message, e.args,
                exc_info=True
            )
            await safe_send(
                chat_id=chat_id,
                context=context,
                text="Сервер временно недоступен, повторите попытку позднее."
            )
            raise ApplicationHandlerStop
    
        bot_data["users"][telegram_id] = db_user
        
        if user_flags is None:
            bot_data["user_flags"][telegram_id] = {
                "is_owner": False,
                "is_admin": False,
                "is_banned": False
            }

        # TODO: Проверка наличия подписки (server) -> флаг (bot)
        # bot_data["user_subscriptions"][subscription.id] = subscription or None
        
    await safe_send(
        update=update,
        text="Выберите действие:",
        reply_markup=menu_keyboard(is_admin=is_admin)
    )
    raise ApplicationHandlerStop

start_command_handler = CommandHandler("start", start)