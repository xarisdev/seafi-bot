from telegram import Update
from telegram.ext import ContextTypes

from ...keyboards.menu import menu_keyboard

from ...models.user import UserCreate
from ...models.exceptions import NotFoundError, APIError

from ...services.api import api_client

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

    data = user.model_dump() | context.bot_data["users"].get(telegram_id, {})
    context.bot_data["users"][telegram_id] = data
    context.user_data["is_auth"] = True

    is_admin = context.bot_data["users"][telegram_id].get("is_admin", False)
    
    await update.message.reply_text(
        "Меню:",
        reply_markup=menu_keyboard(is_admin=is_admin)
    )