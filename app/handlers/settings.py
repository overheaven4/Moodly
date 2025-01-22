from aiogram import Dispatcher
from aiogram.types import Message
from app.handlers.time_picker import start_time_picker


async def change_time_start(message: Message):
    """
    Начало изменения времени уведомлений для зарегистрированного пользователя.
    """
    await start_time_picker(message, action="change_time")


def register_handlers(dp: Dispatcher):
    dp.message.register(change_time_start, commands=["change_time"])
