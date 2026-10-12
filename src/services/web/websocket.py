import json
import asyncio
import logging

from websockets.asyncio.client import connect

from ..payment_handler import ws_handle_payment_result

from ...models.websocket import Payload

from ...app.config import settings

logger = logging.getLogger("websocket")

class WebSocketClient:
    def __init__(self):
        self.application = None
        self.wss_task: asyncio.Task | None = None

    def init_loop(self, application):
        self.application = application
        self.wss_task = asyncio.create_task(
            self._wss_listener_loop()
        )

    async def _wss_listener_loop(self):
        while True:
            try:
                wss_url = f"{settings.WSS_CONNECT_SERVER_URL}?secret_key={settings.X_API_KEY}"

                async with connect(wss_url) as wss:
                    logger.info("WebSocket connected")
                    while True:
                        message = await wss.recv()
                        await self.handler_wss(message)
            
            except Exception as exc:
                logger.error(f"Error websocket connection: {exc}",)
                await asyncio.sleep(5)

    async def handler_wss(self, message: str):
        try:
            data = json.loads(message)
            model = Payload(**data)
        
        except (ValueError, TypeError) as exc:
            logger.warning(
                "Error deserialize websocket message | %s",
                exc,
                exc_info=True
            )
            return

        await handle_payment_result(
            app=self.application,
            payload=model
        )

    async def close(self):
        if self.wss_task:
            self.wss_task.cancel()
            self.wss_task = None

websocket_client = WebSocketClient()