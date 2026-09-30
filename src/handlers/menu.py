from telegram import Update
from telegram.ext import ContextTypes

from ..keyboards.menu import menu_keyboard

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("is_auth") is None:
        await query.edit_message_text(
            text="Для продолжения необходимо зарегистрироваться: /start",
        )
        return

    is_admin = context.bot_data["users"][update.effective_user.id].get("is_admin", False)

    await query.edit_message_text(
        text="Меню:",
        reply_markup=menu_keyboard(is_admin=is_admin),
    )