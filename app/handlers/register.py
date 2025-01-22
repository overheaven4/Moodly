from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from app.handlers.time_picker import start_time_picker


async def register_start(message: Message):
    await start_time_picker(message, action="register")


def register_handlers(dp: Dispatcher):
    dp.message.register(register_start, Command("register"))
