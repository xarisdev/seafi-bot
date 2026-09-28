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
        user = await api_client.create_user(
            UserCreate(
                username=update.effective_user.username,
                telegram_id=telegram_id,
                language="ru"
            )
        )

    except APIError:
        await context.bot.send_message(
            chat_id=telegram_id,
            text="Сервер временно недоступен, повторите попытку позднее."
        )
        return

    context.bot_data["users"][telegram_id] = user.model_dump()
    
    await update.message.reply_text(
        "Меню:",
        reply_markup=menu_keyboard(user.is_premium)
    )