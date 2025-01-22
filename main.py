import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from app.bot import bot
from app.database import setup_database
from app.scheduler import setup_scheduler
from app.handlers import start, register, settings, survey


async def main():
    # Инициализация базы данных
    await setup_database()

    # Настройка бота
    dp = Dispatcher()

    # Регистрация хендлеров
    dp.message.register(start.start_handlers, Command("start"))
    dp.message.register(register.register_start, Command("register"))
    dp.message.register(settings.change_time_start, Command("change_time"))
    dp.message.register(survey.survey_handler, Command("survey"))

    dp.callback_query.register(
        register.register_time, lambda c: c.data.startswith("register:")
    )
    dp.callback_query.register(
        settings.change_time, lambda c: c.data.startswith("change_time:")
    )

    # Настройка планировщика
    setup_scheduler()

    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
