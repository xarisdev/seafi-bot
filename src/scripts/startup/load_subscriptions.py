import logging

from ...client.api_client import api_client
from ...client.models.exceptions import APIException

from ...client.models.api import Subscription

logger = logging.getLogger("scripts.startup.subscriptions")

async def subscriptions_sync(telegram_ids: list[int]) -> dict[int, Subscription]:
    max_count = len(telegram_ids)
    output = {}
    
    for i, telegram_id in enumerate(telegram_ids):
        try:
            subscription = await api_client.get_active_subscription(telegram_id=telegram_id)
            subscription = Subscription(**subscription)

            output[telegram_id] = subscription

            logger.debug("[%s/%s] Load subscription: %s",
                         i, max_count,
                         telegram_id)

        except APIException as exc:
            logger.warning("APIException while load subscription for: %s | Exception: %s",
                           telegram_id,
                           exc.args)

        except Exception as exc:
            logger.exception("Unexpected exception",
                             exc_info=True)

    logger.info("Loaded subscriptions: [%s / %s]", len(output), max_count)

    return output