from aiogram import Dispatcher, types


async def survey_handler(message: types.Message):
    # Заглушка для отправки опроса
    await message.reply("Вот ваш ежедневный опрос:\n\nКак вы себя чувствуете сегодня?")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(survey_handler, commands=["survey"])
