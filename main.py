import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from app.bot import bot
from app.database import setup_database
from app.scheduler import setup_scheduler


async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать! Я помогу отслеживать ваше эмоциональное состояние."
    )


async def main():
    # Инициализация базы данных
    await setup_database()

    # Настройка бота
    dp = Dispatcher()

    # Регистрация хендлеров
    dp.message.register(start_handler, Command("start"))

    # Настройка планировщика
    setup_scheduler()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
