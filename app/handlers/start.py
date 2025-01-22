from aiogram import Dispatcher, types


async def start_handlers(message: types.Message):
    await message.reply(
        "Добро пожаловать! Я помогу отслеживать ваше эмоциональное состояние."
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start"])
