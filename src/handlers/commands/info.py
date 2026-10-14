from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from telegram.constants import ParseMode

from ...keyboards.info_keyboard import info_keyboard

from ...scripts.helpers.bot_info import info_text

async def bot_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=info_text(),
        parse_mode=ParseMode.HTML,
        reply_markup=info_keyboard()
    )

bot_info_command_handler = CommandHandler(
    "info",
    bot_info_command
)