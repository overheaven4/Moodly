from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard():
    """
    Создает клавиатуру с основными командами.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/survey")],
            [KeyboardButton(text="/stats")],
            [KeyboardButton(text="/register")],
            [KeyboardButton(text="/change_time")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard


async def start_handlers(message: types.Message):
    """
    Обработчик команды /start.
    """
    welcome_text = (
        "Добро пожаловать! Я помогу отслеживать ваше эмоциональное состояние.\n\n"
        "Вот основные команды, которые вы можете использовать:\n"
        "/start — показать это сообщение\n"
        "/survey — запустить опрос\n"
        "/stats — просмотреть статистику за неделю\n"
        "/register — зарегистрироваться и выбрать время уведомлений\n"
        "/change_time — изменить время уведомлений"
    )
    await message.reply(welcome_text, reply_markup=get_main_keyboard())


def register_handlers(dp: Dispatcher):
    dp.message.register(start_handlers, Command("start"))
