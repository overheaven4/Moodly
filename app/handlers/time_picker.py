from datetime import time

from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database import get_database_connection


# Универсальная клавиатура выбора времени
def time_picker_keyboard(
    current_hour: int, current_minute: int, action: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="+4ч",
        callback_data=f"{action}:adjust_hour:{current_hour + 4}:{current_minute}",
    )
    builder.button(
        text="+1ч",
        callback_data=f"{action}:adjust_hour:{current_hour + 1}:{current_minute}",
    )
    builder.button(
        text="+5м",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute + 5) % 60}",
    )
    builder.button(
        text="+15м",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute + 15) % 60}",
    )
    builder.adjust(4)

    builder.button(text=f"Часы: {current_hour}", callback_data="noop")
    builder.button(text=f"Мин: {current_minute}", callback_data="noop")
    builder.adjust(2)

    builder.button(
        text="-4ч",
        callback_data=f"{action}:adjust_hour:{current_hour - 4}:{current_minute}",
    )    
    builder.button(
        text="-1ч",
        callback_data=f"{action}:adjust_hour:{current_hour - 1}:{current_minute}",
    )   
    builder.button(
        text="-5м",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute - 5) % 60}",
    ) 
    builder.button(
        text="-15м",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute - 15) % 60}",
    )
    builder.adjust(4)

    # Подтвердить выбор
    builder.button(
        text="✅ Подтвердить",
        callback_data=f"confirm_time:{action}:{current_hour}:{current_minute}",
    )
    builder.adjust(4, 2, 4, 1)
    return builder


# Начало выбора времени
async def start_time_picker(message: Message, action: str):
    initial_hour = 9
    initial_minute = 15

    keyboard = time_picker_keyboard(initial_hour, initial_minute, action)
    await message.answer(
        "Выберите время для уведомлений:", reply_markup=keyboard.as_markup()
    )


# Обработка изменения часов
async def adjust_hour(callback: CallbackQuery):
    action, current_hour, current_minute = (
        callback.data.split(":")[0],
        int(callback.data.split(":")[2]),
        int(callback.data.split(":")[3]),
    )

    keyboard = time_picker_keyboard(current_hour % 24, current_minute, action)
    await callback.message.edit_text(
        f"Выберите время для уведомлений: {current_hour % 24:02d}:{current_minute:02d}",
        reply_markup=keyboard.as_markup(),
    )
    await callback.answer()


# Обработка изменения минут
async def adjust_minute(callback: CallbackQuery):
    action, current_hour, current_minute = (
        callback.data.split(":")[0],
        int(callback.data.split(":")[2]),
        int(callback.data.split(":")[3]),
    )

    keyboard = time_picker_keyboard(current_hour, current_minute, action)
    await callback.message.edit_text(
        f"Выберите время для уведомлений: {current_hour:02d}:{current_minute:02d}",
        reply_markup=keyboard.as_markup(),
    )
    await callback.answer()


# Подтверждение времени
async def confirm_time(callback: CallbackQuery):
    db = await get_database_connection()
    user_id = callback.from_user.id

    # Извлечение данных из callback_data
    data = callback.data.split(":")
    action = data[1]  # Теперь action извлекается правильно
    current_hour = int(data[2])
    current_minute = int(data[3])

    # Формируем время с ведущими нулями
    time_str = f"{current_hour:02d}:{current_minute:02d}:00"  # Всегда добавляем секунды
    selected_time = time.fromisoformat(time_str)

    if action == "register":
        # Регистрация пользователя
        await db.execute(
            """
            INSERT INTO users (id, notification_time)
            VALUES ($1, $2)
            ON CONFLICT (id) DO UPDATE SET notification_time = $2
            """,
            user_id,
            selected_time,
        )
        await callback.message.answer(
            f"Вы успешно зарегистрированы! Выбранное время: {selected_time.strftime('%H:%M')}."
        )
    elif action == "change_time":
        # Обновление времени уведомления
        await db.execute(
            """
            UPDATE users SET notification_time = $1 WHERE id = $2
            """,
            selected_time,
            user_id,
        )
        await callback.message.answer(
            f"Время уведомлений изменено на {selected_time.strftime('%H:%M')}."
        )

    await callback.answer()


# Регистрация хендлеров
def register_handlers(dp: Dispatcher):
    dp.callback_query.register(adjust_hour, lambda c: "adjust_hour" in c.data)
    dp.callback_query.register(adjust_minute, lambda c: "adjust_minute" in c.data)
    dp.callback_query.register(confirm_time, lambda c: "confirm_time" in c.data)
