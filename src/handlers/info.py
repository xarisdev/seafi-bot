from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from telegram.constants import ParseMode

from ..keyboards.info_keyboard import info_keyboard

from ..scripts.helpers.bot_info import info_text

async def bot_info_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text=info_text(),
        parse_mode=ParseMode.HTML,
        reply_markup=info_keyboard()
    )

bot_info_handler = CallbackQueryHandler(
    bot_info_query,
    pattern=r"^bot:info$"
)