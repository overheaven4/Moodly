import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.middleware import FSMContextMiddleware
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from app.bot import bot
from app.database import setup_database
from app.handlers import register, settings, start, survey, time_picker
from app.scheduler import setup_scheduler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomEventIsolation:
    def __init__(self):
        self.locks = {}

    def lock(self, key):
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        return self.locks[key]


async def main():
    await setup_database()

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    events_isolation = CustomEventIsolation()

    dp.update.middleware(
        FSMContextMiddleware(storage=storage, events_isolation=events_isolation)
    )

    start.register_handlers(dp)
    register.register_handlers(dp)
    settings.register_handlers(dp)
    survey.register_handlers(dp)
    time_picker.register_handlers(dp)

    setup_scheduler()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
