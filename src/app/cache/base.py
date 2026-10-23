import json
import logging

import asyncio

from .filters import filters
from .config import BOT_DATA_PATH

from .loader import serialize_data

logger = logging.getLogger("app.cache.base")

class BotDataSaver:
    def __init__(self, path = BOT_DATA_PATH):
        self.bot_data = None
        self.path = path

        self.lock = asyncio.Lock()
        self.task: asyncio.Task | None = None

    async def start(self, bot_data):
        self.bot_data = bot_data

        await self.load()

        self.task = asyncio.create_task(self.run())

    async def stop(self):
        if self.task:
            self.task.cancel()
            
            try:
                await self.task
            
            except asyncio.CancelledError:
                pass

        await self.save()

    async def run(self):
        while True:
            await asyncio.sleep(60)

            try:
                await self.save()

            except Exception:
                logger.exception("Failed to save bot_data")

    async def load(self):
        async with self.lock:
            data = await asyncio.to_thread(
                self.path.read_text,
                encoding="utf-8"
            )
            result = await serialize_data(
                json.loads(data)
            )

            for key, value in result.items():
                self.bot_data[key] = value

    async def save(self):
        async with self.lock:
            output = {}

            for data_filter in filters:
                filtered_data = data_filter.serizalize(self.bot_data)
                output.update(filtered_data)
            
            data = json.dumps(output,
                              ensure_ascii=False,
                              indent=4)
            await asyncio.to_thread(self._write, data)

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(data, encoding="utf-8")

bot_data_saver = BotDataSaver()