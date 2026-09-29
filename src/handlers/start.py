from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards.menu import menu_keyboard

from ..models.user import UserCreate
from ..models.exceptions import (
    NotFoundError, APIError
)

from ..services.api import api_client

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    try:
        user = await api_client.get_user(telegram_id)

    except NotFoundError:
        user = await api_client.create_user(UserCreate(telegram_id=telegram_id))

    except APIError:
        await context.bot.send_message(
            chat_id=telegram_id,
            text="Сервер временно недоступен, повторите попытку позднее."
        )
        return
    
    context.bot_data["users"][telegram_id] = user.model_dump()
    context.user_data["is_auth"] = True
    
    await update.message.reply_text(
        "Меню:",
        reply_markup=menu_keyboard()
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("is_auth") is None:
        await query.edit_message_text(
            text="Для продолжения необходимо зарегистрироваться: /start",
        )
        return

    await query.edit_message_text(
        text="Меню:",
        reply_markup=menu_keyboard(),
    )