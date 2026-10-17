import logging

from typing import TypeVar, Awaitable

from ..client.models.exceptions import APIException, NotFoundError

from .startup.load_plans import load_plans
from .startup.load_superuser import load_superuser

T = TypeVar("T")

logger = logging.getLogger("app.safe_load")

async def _safe_load(
    coroutine: Awaitable[T],
    *,
    default: T,
    message: str
) -> T:
    try:
        return await coroutine
    except NotFoundError:
        logger.warning("%s: not found", message)
    except APIException as e:
        logger.warning("%s: APIError | %s | %s", message, e.status_code, e.message)
    return default

async def synch_superuser(
    application,
    api_client,
    superuser_id,
):
    superuser = await _safe_load(
        load_superuser(api_client, superuser_id),
        default=None,
        message=f"Superuser {superuser_id}"
    )
    if superuser:
        application.bot_data["users"][superuser.telegram_id] = superuser

async def synch_plans(
    application,
    api_client
):
    application.bot_data["plans"] = await _safe_load(
        load_plans(api_client),
        default={},
        message="plans"
    )