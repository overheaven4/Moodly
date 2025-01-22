from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time
from app.database import get_database_connection


# Этапы регистрации
async def register_start(message: Message):
    builder = InlineKeyboardBuilder()
    times = ["09:00", "12:00", "18:00", "21:00"]  # Примеры времени
    for t in times:
        builder.button(text=t, callback_data=f"register:{t}")
    builder.adjust(2)  # Кнопки по 2 в ряд

    await message.answer(
        "Выберите время для получения ежедневных опросов:",
        reply_markup=builder.as_markup(),
    )


# Обработка выбора времени
async def register_time(callback: CallbackQuery, bot: Bot):
    db = await get_database_connection()
    user_id = callback.from_user.id
    selected_time = callback.data.split(":")[1]

    # Сохраняем пользователя в БД
    await db.execute(
        """
        INSERT INTO users (id, notification_time)
        VALUES ($1, $2)
        ON CONFLICT (id) DO UPDATE SET notification_time = $2
        """,
        user_id,
        time.fromisoformat(selected_time),
    )
    await callback.message.answer(
        f"Вы зарегистрированы! Выбранное время: {selected_time}."
    )
    await callback.answer()  # Закрыть всплывающее уведомление


# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.message.register(register_start, Command("register"))
    dp.callback_query.register(register_time, lambda c: c.data.startswith("register:"))
