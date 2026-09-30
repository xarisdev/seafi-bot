from telegram import Update
from telegram.ext import ContextTypes, filters
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler

from ...keyboards.plan import plan_create_exit, plan_create_confirm
from ...keyboards.menu import menu_keyboard

from ...services.api import api_client, APIError
from ...models.plan import SubscriptionPlanCreate

WAITING_OFFER_ID = 0
WAITING_TITLE_DESCRIPTION = 1
WAITING_AMOUNT_USD = 2
WAITING_DURATION_HOURS = 3
WAITING_CONFIRM = 4

async def create_plan_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["plan:create"] = None
    context.user_data["plan:create:message_ids"] = None

    await update.callback_query.edit_message_text(
        "Отмена создания, буфер сброшен",
        reply_markup=menu_keyboard(is_admin=True)
    )

    return ConversationHandler.END

async def create_plan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    is_admin = context.bot_data["users"][telegram_id].get("is_admin", False)
    if not is_admin:
        return ConversationHandler.END

    query = update.callback_query
    await query.answer()

    context.user_data["plan:create"] = {}
    context.user_data["plan:create:message_ids"] = []

    products = await api_client.get_products()
    text = "Доступные продукты\n\n"
    for product in products:
        _text = f"Title: {product.title}\nID: {product.id}\nOfferId: {product.offer_id}\n\n"
        text += _text

    message = await query.edit_message_text(
        text+"Введите offer_id",
        reply_markup=plan_create_exit()
    )
    context.user_data["plan:create:message_ids"].append(message.id)

    return WAITING_OFFER_ID

async def offer_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offer_id = update.message.text.strip()
    if not offer_id:
        context.user_data["plan:create:message_ids"].append(update.message.id)

        await update.message.reply_text(
            "Ошибка получения offer_id, введите еще раз.",
            reply_markup=plan_create_exit()
        )
        return

    context.user_data["plan:create"]["offer_id"] = offer_id

    message = await update.message.reply_text(
        "Введите Заголовок и Описание в формате: title^description",
        reply_markup=plan_create_exit()
    )

    context.user_data["plan:create:message_ids"].append(update.message.id)
    context.user_data["plan:create:message_ids"].append(message.id)

    return WAITING_TITLE_DESCRIPTION

async def title_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    splitted_text = text.split("^", maxsplit=1)

    if len(splitted_text) != 2:
        context.user_data["plan:create:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка разделения Заголовка и Описания, количество фрагментов: {len(splitted_text)}\nРазделитель: {"^" in text}",
            reply_markup=plan_create_exit()
        )
        return

    title = splitted_text[0].strip("\n")
    description = splitted_text[1].strip("\n")
    context.user_data["plan:create"]["title"] = title
    context.user_data["plan:create"]["description"] = description

    message = await update.message.reply_text(
        "Введите стоимость в USD",
        reply_markup=plan_create_exit()
    )

    context.user_data["plan:create:message_ids"].append(update.message.id)
    context.user_data["plan:create:message_ids"].append(message.id)
    
    return WAITING_AMOUNT_USD

async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text.strip()
    try:
        amount_usd = float(amount)
        if amount_usd <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plan:create:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {amount}",
            reply_markup=plan_create_exit()
        )
        return

    context.user_data["plan:create"]["amount_usd"] = amount_usd

    message = await update.message.reply_text(
        "Введите продолжительность в часах",
        reply_markup=plan_create_exit()
    )

    context.user_data["plan:create:message_ids"].append(update.message.id)
    context.user_data["plan:create:message_ids"].append(message.id)

    return WAITING_DURATION_HOURS

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    duration = update.message.text.strip()
    try:
        duration_hours = int(duration)
        if duration_hours <= 0:
            raise ValueError
    except ValueError:
        context.user_data["plan:create:message_ids"].append(update.message.id)

        await update.message.reply_text(
            f"Ошибка конвертации, проверьте ввод: {duration}",
            reply_markup=plan_create_exit()
        )
        return

    context.user_data["plan:create"]["duration_hours"] = duration_hours

    values = [str(v) for v in context.user_data["plan:create"].values()]
    text = "Подтвердите создание плана с параметрами:\n"+"\n".join(values)
    
    message = await update.message.reply_text(
        text,
        reply_markup=plan_create_confirm()
    )

    context.user_data["plan:create:message_ids"].append(update.message.id)

    return WAITING_CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        plan = await api_client.create_plan(
            SubscriptionPlanCreate(**context.user_data["plan:create"])
        )
    except APIError as exc:
        await update.callback_query.edit_message_text(
            f"Ошибка связи с сервером, {exc}",
            reply_markup=plan_create_confirm()
        )
        return

    try: await context.bot.delete_messages(update.effective_user.id, context.user_data["plan:create:message_ids"])
    except: pass

    query = update.callback_query
    await query.answer()

    context.user_data["plan:create"] = None
    context.user_data["plan:create:message_ids"] = None

    await query.edit_message_text(
        f"План создан. ID: {plan.id}",
        reply_markup=menu_keyboard(is_admin=True)
    )
    
    return ConversationHandler.END

conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(create_plan_start, pattern="plan:create")
    ],
    states={
        WAITING_OFFER_ID: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), offer_id_handler)
        ],
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
            CallbackQueryHandler(confirm_handler, pattern="plan:create:confirm")
        ]
    },
    fallbacks=[
        CallbackQueryHandler(create_plan_cancel, pattern="plan:create:exit")
    ]
)