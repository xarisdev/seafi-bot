from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from . import logger as _lg
from .config import settings

from ..models.exceptions import NotFoundError

from ..handlers.start import start
from ..handlers.subscription import (
    subscriptions_list,
    subscription_info
)

from ..services.api import api_client
from ..services.websocket import websocket_client

logger = _lg.logging.getLogger("app.lifespan")

async def on_startup(application: Application):
    api_client.start()
    websocket_client.init_loop()

    try:
        subscriptions = await api_client.get_subscriptions()    
    except NotFoundError:
        subscriptions = []
    application.bot_data["subscriptions"] = subscriptions
    logger.debug("startup success")

async def on_shutdown(application: Application):
    await websocket_client.close()
    await api_client.close()
    logger.debug("shutdown success")

def build_app() -> Application:

    # ------------ Clients ------------

    #websocket = WebSocketClient()

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
            subscriptions_list,
            pattern=r"^sub:list$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            subscription_info,
            pattern=r"^sub:\d+$"
        )
    )

    return application