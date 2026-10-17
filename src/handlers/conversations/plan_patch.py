from telegram import Update
from telegram.ext import ContextTypes, filters
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler

from ...keyboards.plan_keyboard import plan_patch_exit, plan_patch_confirm
from ...keyboards.menu_keyboard import menu_keyboard

from ...client.api_client import api_client
from ...client.models.exceptions import APIException
from ...client.models.api import Plan, PlanUpdate

WAITING_TITLE_DESCRIPTION = 0
WAITING_AMOUNT_USD = 1
WAITING_DURATION_HOURS = 2
WAITING_CONFIRM = 3

# ------------ Scripts ------------

def plan_info_str(plan: Plan):
    text = (
        "Информация:\n\n"
        f"Id: {plan.id}\n"
        f"Title: {plan.title}\n"
        f"Description: {plan.description}\n"
        f"Amount USD: {plan.amount}\n"
        f"Duration H: {plan.duration}\n\n"
    )
    return text

# ------------ Cancel ------------

async def patch_plan_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plans:patch"] = None
    context.user_data["plans:patch:message_ids"] = None

    await update.callback_query.edit_message_text(
        "Отмена редактирования, буфер сброшен",
        reply_markup=menu_keyboard(is_admin=True)
    )

    return ConversationHandler.END

# ------------ Start ------------

async def patch_plan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    query = update.callback_query
    await query.answer()

    if not context.bot_data["users"][telegram_id].get("is_admin", False):
        return ConversationHandler.END

    context.user_data["plans:patch:message_ids"] = []

    plan_id = query.data.split(":")[-1]
    plan: Plan = context.bot_data["plans"][int(plan_id)]
    context.user_data["plans:patch"] = plan
    
    message = await query.edit_message_text(
        plan_info_str(plan)+"Введите Заголовок и Описание в формате: title^description",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plans:patch:message_ids"].append(message.id)

    return WAITING_TITLE_DESCRIPTION

async def title_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    splitted_text = text.split("^", maxsplit=1)

    if len(splitted_text) != 2:
        context.user_data["plans:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка разделения Заголовка и Описания, количество фрагментов: {len(splitted_text)}\nРазделитель: {"^" in text}",
            reply_markup=plan_patch_exit()
        )
        return

    title = splitted_text[0].strip("\n")
    description = splitted_text[1].strip("\n")
    context.user_data["plans:patch"].title = title
    context.user_data["plans:patch"].description = description

    message = await update.message.reply_text(
        plan_info_str(context.user_data["plans:patch"]) + "Введите стоимость в USD",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plans:patch:message_ids"].append(update.message.id)
    context.user_data["plans:patch:message_ids"].append(message.id)
    
    return WAITING_AMOUNT_USD

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text.strip()
    try:
        amount_usd = float(amount)
        if amount_usd <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plans:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {amount}",
            reply_markup=plan_patch_exit()
        )
        return

    context.user_data["plans:patch"].amount = amount_usd

    message = await update.message.reply_text(
        plan_info_str(context.user_data["plans:patch"])+"Введите продолжительность в часах",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plans:patch:message_ids"].append(update.message.id)
    context.user_data["plans:patch:message_ids"].append(message.id)

    return WAITING_DURATION_HOURS

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    duration = update.message.text.strip()
    try:
        duration_hours = int(duration)
        if duration_hours <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plans:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {duration}",
            reply_markup=plan_patch_exit()
        )
        return

    context.user_data["plans:patch"].duration = duration_hours
    
    message = await update.message.reply_text(
        plan_info_str(context.user_data["plans:patch"])+"Подтвердите изменение",
        reply_markup=plan_patch_confirm()
    )

    context.user_data["plans:patch:message_ids"].append(update.message.id)

    return WAITING_CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        plan_update: Plan = context.user_data["plans:patch"]
        plan = await api_client.patch_plan(
            plan_id=plan_update.id,
            data=PlanUpdate(**plan_update.model_dump())
        )
    except APIException:
        await update.callback_query.edit_message_text(
            f"Сервер вернул ошибку",
            reply_markup=plan_patch_confirm()
        )
        return

    try: await context.bot.delete_messages(update.effective_user.id, context.user_data["plans:patch:message_ids"])
    except: pass

    context.user_data["plans:patch"] = None
    context.user_data["plans:patch:message_ids"] = None

    await query.edit_message_text(
        f"План изменен. ID: {plan.id}",
        reply_markup=menu_keyboard(is_admin=True)
    )
    
    return ConversationHandler.END

conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(patch_plan_start, pattern="plans:patch")
    ],
    states={
        WAITING_TITLE_DESCRIPTION: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), title_description_handler)
        ],
        WAITING_AMOUNT_USD: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), amount_handler)
        ],
        WAITING_DURATION_HOURS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), duration_handler)
        ],
        WAITING_CONFIRM: [
            CallbackQueryHandler(confirm_handler, pattern="plans:patch:confirm")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(patch_plan_cancel, pattern="plans:patch:exit")
    ]
)