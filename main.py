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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Кастомная реализация events_isolation
class CustomEventIsolation:
    def __init__(self):
        self.locks = {}

    def lock(self, key):
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        return self.locks[key]


async def main():
    # Инициализация базы данных
    await setup_database()

    # Настройка хранилища и диспетчера
    storage = MemoryStorage()  # Хранилище для FSM
    dp = Dispatcher(storage=storage)

    # Создаем экземпляр кастомной изоляции событий
    events_isolation = CustomEventIsolation()

    # Подключение Middleware для FSM
    dp.update.middleware(
        FSMContextMiddleware(storage=storage, events_isolation=events_isolation)
    )

    # Регистрация хендлеров
    start.register_handlers(dp)
    register.register_handlers(dp)
    settings.register_handlers(dp)
    survey.register_handlers(dp)  # Регистрация обработчиков опроса
    time_picker.register_handlers(dp)

    # Настройка планировщика
    setup_scheduler()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
