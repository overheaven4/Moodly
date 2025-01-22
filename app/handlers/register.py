from aiogram import Dispatcher
from aiogram.types import Message
from app.handlers.time_picker import start_time_picker


async def register_start(message: Message):
    """
    Начало регистрации пользователя. Пользователь выбирает время для уведомлений.
    """
    await start_time_picker(message, action="register")


def register_handlers(dp: Dispatcher):
    dp.message.register(register_start, commands=["register"])
