from aiogram import Dispatcher, types
from aiogram.filters import Command


async def start_handlers(message: types.Message):
    await message.reply(
        "Добро пожаловать! Я помогу отслеживать ваше эмоциональное состояние."
    )


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handlers, Command("start"))
