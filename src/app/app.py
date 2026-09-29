from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from . import logger as _lg
from .config import settings

from ..models.exceptions import NotFoundError

from ..handlers.start import start, menu
from ..handlers.plan import (
    plans_list,
    plan_info
)

from ..services.api import api_client
from ..services.websocket import websocket_client

logger = _lg.logging.getLogger("app.lifespan.cycle")

async def on_startup(application: Application):
    api_client.start()
    websocket_client.init_loop()

    try:
        plans = await api_client.get_plans()    
    except NotFoundError:
        plans = []
    application.bot_data["plans"] = plans
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

    # ------------ Handlers ------------

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(
            menu,
            pattern=r"^menu:main$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            plans_list,
            pattern=r"^plan:list$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            plan_info,
            pattern=r"^plan:\d+$"
        )
    )

    return application