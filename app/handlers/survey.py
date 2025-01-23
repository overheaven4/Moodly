import io
import logging
import statistics
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (BufferedInputFile, InputFile, KeyboardButton,
                           ReplyKeyboardMarkup)

from app.database import get_database_connection
from app.handlers.start import get_main_keyboard

# Настройка логирования
logger = logging.getLogger(__name__)


# Определяем состояние для опроса
class SurveyState(StatesGroup):
    in_progress = State()


# Тексты кнопок
BUTTON_TEXTS = {
    1: "печалька(1)",
    2: "грусть(2)",
    3: "безразличие(3)",
    4: "хорошо(4)",
    5: "отлично(5)",
}

# Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BUTTON_TEXTS[1])],
        [KeyboardButton(text=BUTTON_TEXTS[2])],
        [KeyboardButton(text=BUTTON_TEXTS[3])],
        [KeyboardButton(text=BUTTON_TEXTS[4])],
        [KeyboardButton(text=BUTTON_TEXTS[5])],
    ],
    resize_keyboard=True,
)


async def create_mood_chart(results):
    """
    Создает график настроения за последнюю неделю.
    Возвращает изображение в виде байтов.
    """
    if not results:
        return None

    # Подготовка данных
    dates = [row["created_at"] for row in results]
    moods = [row["answer"] for row in results]

    # Создание графика
    plt.figure(figsize=(10, 5))
    plt.plot(dates, moods, marker="o", linestyle="-", color="b")
    plt.title("График настроения за неделю")
    plt.xlabel("Дата")
    plt.ylabel("Настроение")
    plt.yticks(range(1, 6), [BUTTON_TEXTS[i] for i in range(1, 6)])  # Подписи для оси Y
    plt.grid(True)

    # Сохранение графика в байты
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return buf


async def calculate_mood_trend(results):
    """
    Анализирует тренд настроения за неделю.
    """
    if not results:
        return "нет данных"

    # Разделяем ответы на две половины недели
    mid_point = len(results) // 2
    first_half = results[:mid_point]
    second_half = results[mid_point:]

    # Среднее настроение за первую и вторую половину недели
    avg_first_half = (
        sum(row["answer"] for row in first_half) / len(first_half) if first_half else 0
    )
    avg_second_half = (
        sum(row["answer"] for row in second_half) / len(second_half)
        if second_half
        else 0
    )

    if avg_second_half > avg_first_half:
        return "положительный"
    elif avg_second_half < avg_first_half:
        return "отрицательный"
    else:
        return "стабильный"


async def calculate_mood_stability(results):
    """
    Вычисляет стандартное отклонение настроения.
    """
    if not results:
        return None

    answers = [row["answer"] for row in results]
    return statistics.stdev(answers) if len(answers) > 1 else 0


async def calculate_weighted_average(results):
    """
    Вычисляет взвешенное среднее настроение.
    """
    total_weighted_sum = 0
    total_weight = 0

    for row in results:
        created_at = row["created_at"]
        answer = row["answer"]

        # Вес зависит от давности ответа
        days_ago = (datetime.now() - created_at).days
        if days_ago <= 2:
            weight = 1.5  # Больший вес для свежих ответов
        else:
            weight = 1.0

        total_weighted_sum += answer * weight
        total_weight += weight

    if total_weight == 0:
        return None  # Если нет данных

    return total_weighted_sum / total_weight


async def send_stats(message: types.Message):
    """
    Отправляет расширенную статистику настроений за последнюю неделю и график.
    """
    db = await get_database_connection()
    try:
        user_id = message.from_user.id
        # Получаем записи за последнюю неделю
        results = await db.fetch(
            """
            SELECT answer, created_at FROM survey_results
            WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
            ORDER BY created_at
            """,
            user_id,
        )

        if results:
            # Формируем статистику с текстами кнопок
            stats = "\n".join(
                [
                    f"{row['created_at']}: {BUTTON_TEXTS[row['answer']]}"
                    for row in results
                ]
            )

            # Взвешенное среднее настроение
            weighted_avg = await calculate_weighted_average(results)
            weighted_avg_text = (
                BUTTON_TEXTS[round(weighted_avg)] if weighted_avg else "нет данных"
            )

            # Тренд настроения
            trend = await calculate_mood_trend(results)

            # Эмоциональная стабильность
            stability = await calculate_mood_stability(results)
            stability_text = (
                f"{stability:.2f}" if stability is not None else "нет данных"
            )

            # Формируем итоговое сообщение
            message_text = (
                f"Ваша статистика за последнюю неделю:\n{stats}\n\n"
                f"Взвешенное среднее настроение: {weighted_avg_text}\n"
                f"Тренд настроения: {trend}\n"
                f"Эмоциональная стабильность: {stability_text}"
            )
            await message.reply(message_text)

            # Создаем и отправляем график
            chart = await create_mood_chart(results)
            if chart:
                await message.answer_photo(
                    photo=BufferedInputFile(
                        chart.getvalue(), filename="mood_chart.png"
                    ),
                    caption="График вашего настроения за неделю:",
                )
        else:
            await message.reply("У вас нет записей за последнюю неделю.")
    except Exception as e:
        logger.error(f"Ошибка при отправке статистики: {e}")
        await message.reply("Произошла ошибка при получении статистики.")
    finally:
        await db.close()


# Функция для отправки опроса
async def survey_handler(message: types.Message, state: FSMContext):
    """
    Запускает опрос для пользователя.
    """
    user_id = message.from_user.id
    logger.info(f"Запуск опроса для пользователя {user_id}")
    await message.reply(
        "Как вы себя чувствуете сегодня? Выберите смайлик:", reply_markup=keyboard
    )
    await state.set_state(SurveyState.in_progress)
    logger.info(f"Состояние установлено для пользователя {user_id}")


# Обработчик нажатия кнопки
async def handle_survey_response(message: types.Message, state: FSMContext):
    """
    Обрабатывает ответ пользователя на опрос.
    """
    logger.info("Обработчик handle_survey_response вызван")
    # Сохраняем результат в базе данных
    mood = None

    if message.text == BUTTON_TEXTS[1]:
        mood = 1
    elif message.text == BUTTON_TEXTS[2]:
        mood = 2
    elif message.text == BUTTON_TEXTS[3]:
        mood = 3
    elif message.text == BUTTON_TEXTS[4]:
        mood = 4
    elif message.text == BUTTON_TEXTS[5]:
        mood = 5

    logger.info(f"Определённое настроение: {mood}")

    if mood:
        try:
            db = await get_database_connection()
            user_id = message.from_user.id

            user_exists = await db.fetchval(
                """
                SELECT id FROM users WHERE id = $1
                """,
                user_id,
            )

            if not user_exists:
                await message.reply(
                    "Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь с помощью команды /register."
                )
                return  # Прерываем выполнение функции, если пользователь не зарегистрирован

            # Сохраняем настроение в базу данных как новую запись
            logger.info(f"Сохранение настроения пользователя {user_id}: {mood}")
            await db.execute(
                """
                INSERT INTO survey_results (user_id, answer)
                VALUES ($1, $2)
                """,
                user_id,
                mood,
            )
            await message.reply(
                f"Спасибо за ваш ответ! Ваше настроение: {BUTTON_TEXTS[mood]}",
                reply_markup=get_main_keyboard(),  # Отправляем клавиатуру с командами
            )

            # Завершаем опрос, удаляем состояние
            await state.clear()
            logger.info(f"Состояние очищено для пользователя {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении в БД: {e}")
            await message.reply(
                "Произошла ошибка при сохранении вашего ответа. Пожалуйста, попробуйте позже.",
                reply_markup=get_main_keyboard(),  # Отправляем клавиатуру с командами
            )
    else:
        logger.warning(
            f"Пользователь {message.from_user.id} выбрал неверный вариант: {message.text}"
        )
        await message.reply(
            "Пожалуйста, выберите один из предложенных смайликов.",
            reply_markup=get_main_keyboard(),  # Отправляем клавиатуру с командами
        )


# Регистрируем хэндлеры
def register_handlers(dp: Dispatcher):
    dp.message.register(survey_handler, Command("survey"))
    dp.message.register(handle_survey_response, SurveyState.in_progress)
    dp.message.register(send_stats, Command("stats"))
