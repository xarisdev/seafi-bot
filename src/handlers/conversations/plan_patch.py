from telegram import Update
from telegram.ext import ContextTypes, filters
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler

from ...keyboards.plan import plan_patch_exit, plan_patch_confirm
from ...keyboards.menu import menu_keyboard

from ...services.api import api_client, APIError
from ...models.plan import SubscriptionPlanUpdate, SubscriptionPlanRead

WAITING_TITLE_DESCRIPTION = 0
WAITING_AMOUNT_USD = 1
WAITING_DURATION_HOURS = 2
WAITING_CONFIRM = 3

# ------------ Scripts ------------

def plan_info_str(plan: SubscriptionPlanRead):
    text = (
        "Информация:\n\n"
        f"Id: {plan.id}\n"
        f"Title: {plan.title}\n"
        f"Description: {plan.description}\n"
        f"Amount USD: {plan.amount_usd}\n"
        f"Duration H: {plan.duration_hours}\n\n"
    )
    return text

# ------------ Cancel ------------

async def patch_plan_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plan:patch"] = None
    context.user_data["plan:patch:message_ids"] = None

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

    context.user_data["plan:patch:message_ids"] = []

    plan_id = query.data.split(":")[-1]
    plan: SubscriptionPlanRead = context.bot_data["plans"][int(plan_id)]
    context.user_data["plan:patch"] = plan
    
    message = await query.edit_message_text(
        plan_info_str(plan)+"Введите Заголовок и Описание в формате: title^description",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plan:patch:message_ids"].append(message.id)

    return WAITING_TITLE_DESCRIPTION

async def title_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    splitted_text = text.split("^", maxsplit=1)

    if len(splitted_text) != 2:
        context.user_data["plan:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка разделения Заголовка и Описания, количество фрагментов: {len(splitted_text)}\nРазделитель: {"^" in text}",
            reply_markup=plan_patch_exit()
        )
        return

    title = splitted_text[0].strip("\n")
    description = splitted_text[1].strip("\n")
    context.user_data["plan:patch"].title = title
    context.user_data["plan:patch"].description = description

    message = await update.message.reply_text(
        plan_info_str(context.user_data["plan:patch"]) + "Введите стоимость в USD",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plan:patch:message_ids"].append(update.message.id)
    context.user_data["plan:patch:message_ids"].append(message.id)
    
    return WAITING_AMOUNT_USD

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text.strip()
    try:
        amount_usd = float(amount)
        if amount_usd <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plan:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {amount}",
            reply_markup=plan_patch_exit()
        )
        return

    context.user_data["plan:patch"].amount_usd = amount_usd

    message = await update.message.reply_text(
        plan_info_str(context.user_data["plan:patch"])+"Введите продолжительность в часах",
        reply_markup=plan_patch_exit()
    )

    context.user_data["plan:patch:message_ids"].append(update.message.id)
    context.user_data["plan:patch:message_ids"].append(message.id)

    return WAITING_DURATION_HOURS

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    duration = update.message.text.strip()
    try:
        duration_hours = int(duration)
        if duration_hours <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plan:patch:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {duration}",
            reply_markup=plan_patch_exit()
        )
        return

    context.user_data["plan:patch"].duration_hours = duration_hours
    
    message = await update.message.reply_text(
        plan_info_str(context.user_data["plan:patch"])+"Подтвердите изменение",
        reply_markup=plan_patch_confirm()
    )

    context.user_data["plan:patch:message_ids"].append(update.message.id)

    return WAITING_CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        plan_update: SubscriptionPlanRead = context.user_data["plan:patch"]
        plan = await api_client.patch_plan(
            plan_id=plan_update.id,
            data=SubscriptionPlanUpdate(**plan_update.model_dump())
        )
    except APIError as exc:
        await update.callback_query.edit_message_text(
            f"Ошибка связи с сервером, {exc}",
            reply_markup=plan_patch_confirm()
        )
        return

    try: await context.bot.delete_messages(update.effective_user.id, context.user_data["plan:patch:message_ids"])
    except: pass

    context.user_data["plan:patch"] = None
    context.user_data["plan:patch:message_ids"] = None

    await query.edit_message_text(
        f"План изменен. ID: {plan.id}",
        reply_markup=menu_keyboard(is_admin=True)
    )
    
    return ConversationHandler.END

conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(patch_plan_start, pattern="plan:patch")
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
            CallbackQueryHandler(confirm_handler, pattern="plan:patch:confirm")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(patch_plan_cancel, pattern="plan:patch:exit")
    ]
)