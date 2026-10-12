import asyncio
import logging

from collections import defaultdict

from telegram.ext import Application

from .config import settings

from ..security.verify_user import verify_handler

from ..services.web.api import api_client
from ..services.web.websocket import websocket_client

from ..scripts.utils import safe_load
from ..scripts.startup.load_superuser import load_superuser
from ..scripts.startup.load_plans import load_plans

from ..handlers.commands.start import start_command_handler
from ..handlers.menu import menu_handler
from ..handlers.plans import (
    plans_list_handler,
    plans_setup_handler,
    selected_plan_info_handler,
    select_payment_methods_handler,
    selected_payment_method_handler
)
from ..handlers.payment import (
    payment_check_handler,
    payment_cancel_handler
)
from ..handlers.conversations.plan_create import conversation as plan_create_conversation
from ..handlers.conversations.plan_patch import conversation as plan_patch_conversation

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger("app.lifecycle")

async def on_startup(app: Application):
    api_client.start()
    websocket_client.init_loop(app)

    # ------------ Synchronization ------------
    
    superuser = await safe_load(
        load_superuser(api_client, settings.ADMIN_ID),
        default=None,
        msg=f"superuser {settings.ADMIN_ID}"
    )
    if superuser:
        app.bot_data["users"][settings.ADMIN_ID] = superuser

    app.bot_data["plans"] = await safe_load(
        load_plans(api_client),
        default={},
        msg="plans"
    )
    
    logger.debug("startup success")

async def on_shutdown(app: Application):
    await websocket_client.close()
    await api_client.close()

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

    application.bot_data["users"] = {}

    application.bot_data["user_flags"] = {}
    application.bot_data["user_flags"][settings.ADMIN_ID] = {
        "is_owner": True,
        "is_admin": True,
        "is_banned": False
    }
    
    application.bot_data["user_subscriptions"] = {}

    application.bot_data["plans"] = {}
    application.bot_data["invoices"] = {}

    application.bot_data["payment_msgs"] = {}
    # ------------ Handlers ------------
    
    application.add_handler(start_command_handler, group=-2)
    application.add_handler(verify_handler, group=-1)

    application.add_handler(plan_create_conversation)
    application.add_handler(plan_patch_conversation)

    application.add_handler(menu_handler)
    application.add_handler(plans_list_handler)
    application.add_handler(plans_setup_handler)
    application.add_handler(selected_plan_info_handler)
    application.add_handler(select_payment_methods_handler)
    application.add_handler(selected_payment_method_handler)

    application.add_handler(payment_check_handler)
    application.add_handler(payment_cancel_handler)

    return application