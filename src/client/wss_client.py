import logging
import asyncio

import json

from telegram.ext import Application

from websockets.asyncio.client import connect
from .models.api import WebSocketMessage

from ..services.payment_handler import check_payment_at_wss

from ..app.config import settings

logger = logging.getLogger("client.wss:_client")

class WSSClient():
    CONNECT_URL = f"{settings.WSS_CONNECT_SERVER_URL}"
    SECRET_KEY = f"?secret_key={settings.X_API_KEY}"
    RECONNECT_TIMER = 5

    def __init__(self):
        self.application: Application = None
        self.wss_task: asyncio.Task | None = None

    def start(self, application):
        self.application = application
        self.wss_task = asyncio.create_task(
            self._wss_listener_loop()
        )

    async def close(self):
        if self.wss_task:
            self.wss_task.cancel()
            self.wss_task = None

    async def _wss_listener_loop(self):
        while True:
            try:
                wss_url = self.CONNECT_URL + self.SECRET_KEY

                async with connect(wss_url) as wss:
                    logger.info("WebSocket connected")
                    while True:
                        message = await wss.recv()
                        model = await self._deserizalize(message)
                        await self.handle(model)

            except Exception as exc:
                logger.error(
                    "Error websocket connection: %s",
                    exc
                )
                logger.info(
                    "Websocket reconnection in %s s.",
                    self.RECONNECT_TIMER
                )
                await asyncio.sleep(self.RECONNECT_TIMER)

    async def _deserizalize(self, message: str) -> WebSocketMessage:
        try:
            data = json.loads(message)
            model = WebSocketMessage(**data)

        except (ValueError, TypeError) as exc:
            logger.warning(
                "Error deserialize websocket message | %s",
                exc,
                exc_info=True
            )
            return
        
        return model

    async def handle(self, message: WebSocketMessage):
        exists = self.application.bot_data["recieved_websockets"].get(message.id)
        if exists:
            logger.info("Recieve duplicate websocket [%s]",
                        message.id)
            return

        logger.info(
            "Recieve websocket: %s",
            message.model_dump()
        )

        self.application.bot_data["recieved_websockets"][message.id] = message.model_dump(mode="json")

        await check_payment_at_wss(
            application=self.application,
            message=message
        )

wss_client = WSSClient()