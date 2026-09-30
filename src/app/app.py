from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from . import logger as _lg
from .config import settings

from ..models.exceptions import NotFoundError

from ..handlers.commands.start import start
from ..handlers.menu import menu
from ..handlers.plan import (
    plans_list,
    plans_setup,
    plan_info
)
from ..handlers.conversations.plan_create import conversation as plan_create_conversation
from ..handlers.conversations.plan_patch import conversation as plan_patch_conversation

from ..services.api import api_client
from ..services.websocket import websocket_client

logger = _lg.logging.getLogger("app.lifespan.cycle")

async def on_startup(application: Application):
    api_client.start()
    websocket_client.init_loop()

    application.bot_data["plans"] = {}
    try:
        plans = await api_client.get_plans()    
    except NotFoundError:
        plans = []

    for plan in plans:
        application.bot_data["plans"][plan.id] = plans
    
    logger.debug("startup success")

async def on_shutdown(application: Application):
    await websocket_client.close()
    await api_client.close()
    logger.debug("shutdown success")

def build_app() -> Application:

    # ------------ Build ------------

    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    # ------------ Global ------------

    application.bot_data["users"] = {}
    application.bot_data["users"][settings.ADMIN_ID] = {"is_admin": True}

    # ------------ Handlers ------------

    application.add_handler(CommandHandler("start", start))

    application.add_handler(plan_create_conversation)
    application.add_handler(plan_patch_conversation)

    application.add_handler(
        CallbackQueryHandler(menu, pattern=r"^menu:main$")
    )
    application.add_handler(
        CallbackQueryHandler(plans_list, pattern=r"^plan:list$")
    )
    application.add_handler(
        CallbackQueryHandler(plans_setup, pattern=r"^plan:setup$")
    )
    application.add_handler(
        CallbackQueryHandler(plan_info, pattern=r"^plan:\d+$")
    )

    return application