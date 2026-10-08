from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from ..keyboards.menu import menu_keyboard

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    bot_data = context.bot_data

    telegram_id = update.effective_user.id
    
    is_admin = bot_data["user_flags"][telegram_id]["is_admin"]

    await query.edit_message_text(
        text="Выберите действие:",
        reply_markup=menu_keyboard(is_admin=is_admin),
    )

menu_handler = CallbackQueryHandler(menu, pattern=r"^menu:main$")