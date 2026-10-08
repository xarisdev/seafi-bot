import json

import asyncio
import logging

from websockets.asyncio.client import connect

from ..app.config import settings

from .payment_handler import handle_payment_result

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
        return # TODO
        data = json.loads(message)

        telegram_id = data["telegram_id"]
        payload = data["payload"]

        r_invoice_id = payload["invoice_id"]

        invoice = self.application.bot_data["invoices"].get(telegram_id)
        if invoice is None:
            logger.warning(f"Invoice not found for telegram_id: {telegram_id}")
            return

        if invoice.id != r_invoice_id:
            logger.warning(f"Unexpected invoice_id: {r_invoice_id}")
            return

        await handle_payment_result(
            app=self.application,
            telegram_id=telegram_id,
            payload=payload
        )

    async def close(self):
        if self.wss_task:
            self.wss_task.cancel()
            self.wss_task = None

websocket_client = WebSocketClient()