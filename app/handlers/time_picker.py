from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import time
from app.database import get_database_connection


# Универсальная клавиатура выбора времени
def time_picker_keyboard(
    current_hour: int, current_minute: int, action: str
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    # Часы
    builder.button(text=f"Часы: {current_hour}", callback_data="noop")
    builder.button(
        text="➖",
        callback_data=f"{action}:adjust_hour:{current_hour - 1}:{current_minute}",
    )
    builder.button(
        text="➕",
        callback_data=f"{action}:adjust_hour:{current_hour + 1}:{current_minute}",
    )
    builder.adjust(3)

    # Минуты
    builder.button(text=f"Минуты: {current_minute}", callback_data="noop")
    builder.button(
        text="➖",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute - 15) % 60}",
    )
    builder.button(
        text="➕",
        callback_data=f"{action}:adjust_minute:{current_hour}:{(current_minute + 15) % 60}",
    )
    builder.adjust(3)

    # Подтвердить выбор
    builder.button(
        text="✅ Подтвердить",
        callback_data=f"confirm_time:{action}:{current_hour}:{current_minute}",
    )

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
        0,
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
        int(
            callback.data.split(":")[3]
        ),  # Теперь минут тоже передаются в callback_data
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

    # Формируем время
    time_str = f"{current_hour}:{current_minute}"
    # Добавляем ':00' если секунд нет
    if len(time_str.split(":")) == 2:
        time_str += ":00"
    if len(time_str.split(":")[0]) != 2:
        time_str = f"0{time_str}"
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
