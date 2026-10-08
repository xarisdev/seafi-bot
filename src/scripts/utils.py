import logging

from typing import TypeVar, Awaitable, Callable

from ..models.exceptions import APIError, NotFoundError

T = TypeVar("T")

logger = logging.getLogger("app.safe_load")

async def safe_load(
    coroutine: Awaitable[T],
    *,
    default: T,
    msg: str
) -> T:
    try:
        return await coroutine
    except NotFoundError:
        logger.warning("%s: not found", msg)
    except APIError as e:
        logger.warning("%s: APIError | %s | %s", msg, e.status_code, e.message)
    return default