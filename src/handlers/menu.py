from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards.menu import menu_keyboard

from ..services.api import api_client
from ..models.exceptions import NotFoundError

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id

    if context.user_data.get("is_auth") is None:
        try:
            user = await api_client.get_user(telegram_id)
            context.user_data["is_auth"] = True

            #sub = await api_client.get_subscription(telegram_id)
            
            bot_data = context.bot_data["users"].get(telegram_id, {})
            context.bot_data["users"][telegram_id] = bot_data | user.model_dump()
        
        except NotFoundError:
            await query.edit_message_text(
                text="Для продолжения необходимо зарегистрироваться: /start",
            )
            return

    is_admin = context.bot_data["users"][telegram_id].get("is_admin", False)

    await query.edit_message_text(
        text="Меню:",
        reply_markup=menu_keyboard(is_admin=is_admin),
    )