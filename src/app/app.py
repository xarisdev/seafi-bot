import asyncio
import logging

from collections import defaultdict

from telegram.ext import Application

from ..client.api_client import api_client
from ..client.wss_client import wss_client

from ..scripts.utils import synch_superuser, synch_plans

from ..handlers import handlers

from .config import settings

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("app.lifecycle")

async def on_startup(app: Application):
    api_client.startup(application=app)
    wss_client.start(application=app)

    await synch_superuser(
        application=app,
        api_client=api_client,
        superuser_id=settings.ADMIN_ID
    )

    await synch_plans(
        application=app,
        api_client=api_client
    )
    
    logger.debug("startup success")


async def on_shutdown(app: Application):
    await wss_client.close()
    await api_client.shutdown()

    logger.debug("shutdown success")


# ------------ Build ------------

def build_application() -> Application:
    logger.info("Building application")

    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    # ------------ Global ------------

    application.bot_data['locks'] = defaultdict(asyncio.Lock)

    application.bot_data["plans"] = {}
    application.bot_data["recieved_websockets"] = {}

    application.bot_data["users"] = {}
    application.bot_data["subscriptions"] = {}
    application.bot_data["pending_invoices"] = {}

    application.bot_data["user_flags"] = {}
    application.bot_data["user_flags"][settings.ADMIN_ID] = {
        "is_owner": True,
        "is_admin": True,
        "is_banned": False
    }

    application.bot_data["payment_messages"] = {}
    application.bot_data["payment_keyboard"] = {}

    # ------------ Handlers ------------
    
    application.add_handlers(handlers=handlers)

    return application