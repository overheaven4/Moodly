from aiogram import Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database import get_database_connection
from datetime import time


# Этапы изменения времени
async def change_time_start(message: Message):
    builder = InlineKeyboardBuilder()
    times = ["09:00", "12:00", "18:00", "21:00"]  # Примеры времени
    for t in times:
        builder.button(text=t, callback_data=f"change_time:{t}")
    builder.adjust(2)

    await message.answer(
        "Выберите новое время для получения опросов:", reply_markup=builder.as_markup()
    )


# Обработка выбора нового времени
async def change_time(callback: CallbackQuery):
    db = await get_database_connection()
    user_id = callback.from_user.id
    new_time = callback.data.split(":")[1]

    # Обновляем время уведомления
    await db.execute(
        """
        UPDATE users SET notification_time = $1 WHERE id = $2
        """,
        time.fromisoformat(new_time),
        user_id,
    )
    await callback.message.answer(f"Время уведомлений изменено на {new_time}.")
    await callback.answer()


# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.message.register(change_time_start, Command("change_time"))
    dp.callback_query.register(change_time, lambda c: c.data.startswith("change_time:"))
