import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import mplcyberpunk
from aiogram import Bot
from aiogram.types import (
    BufferedInputFile,
    InputFile,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot import bot
from app.database import get_database_connection
from app.handlers.survey import (
    BUTTON_TEXTS,
    WEEKDAYS,
    a,
    calculate_mood_stability,
    calculate_mood_trend,
    calculate_weighted_average,
    crat,
    create_mood_chart,
    delta,
    negative_motivations,
    positive_motivations,
)

scheduler = AsyncIOScheduler()
plt.style.use("cyberpunk")


async def send_daily_survey():
    db = await get_database_connection()
    try:
        users = await db.fetch("SELECT id, notification_time FROM users")
        for user in users:
            user_id = user["id"]
            notification_time = user["notification_time"]

            now = datetime.now().time()
            if (
                now.hour == notification_time.hour
                and now.minute == notification_time.minute
            ):
                await bot.send_message(
                    user_id,
                    "Самое время пройти ежедневный опрос!\nИспользуйте команду /survey",
                )
    except Exception as e:
        print(f"Ошибка при отправке ежедневного опроса: {e}")
    finally:
        await db.close()


async def send_weekly_statistics():

    db = await get_database_connection()
    try:
        users = await db.fetch("SELECT id FROM users")
        for user in users:
            try:
                user_id = user["id"]

                results = await db.fetch(
                    """
                    SELECT answer, created_at
                    FROM survey_results
                    WHERE user_id = $1
                    AND created_at >= NOW() - INTERVAL '7 days'
                    ORDER BY created_at
                    """,
                    user_id,
                )

                if results:

                    stats = "\n".join(
                        [
                            f"{(row[crat] + delta).strftime(f'{WEEKDAYS[(row[crat] + delta).strftime(a)]} %d.%m, %H:%M')} - {BUTTON_TEXTS[row['answer']]}"
                            for row in results
                        ]
                    )

                    weighted_avg = await calculate_weighted_average(results)
                    if weighted_avg:
                        weighted_avg_text = BUTTON_TEXTS[round(weighted_avg)]
                    else:
                        weighted_avg_text = "нет данных"

                    trend = await calculate_mood_trend(results)

                    if trend == "отрицательный" or (
                        weighted_avg and round(weighted_avg) in [1, 2]
                    ):
                        phrase = random.choice(negative_motivations)
                    else:
                        phrase = random.choice(positive_motivations)

                    stability = await calculate_mood_stability(results)
                    if stability is not None:
                        stability_text = f"{stability:.2f}"
                    else:
                        stability_text = "нет данных"

                    message_text = (
                        f"Ваша статистика за последнюю неделю:\n{stats}\n\n"
                        f"Взвешенное среднее настроение: {weighted_avg_text}\n"
                        f"Тренд настроения: {trend}\n"
                        f"Эмоциональная стабильность: {stability_text}"
                    )

                    await bot.send_message(user_id, message_text)
                    chart = await create_mood_chart(results)
                    if chart:
                        await bot.send_photo(
                            user_id,
                            photo=BufferedInputFile(
                                chart.getvalue(), filename="mood_chart.png"
                            ),
                            caption="График вашего настроения за неделю:",
                        )
                        await bot.send_message(user_id, phrase)

                else:

                    await bot.send_message(
                        user_id, "У вас нет записей за последнюю неделю."
                    )
            except Exception as e:
                print(f"Ошибка при отправке статистики для пользователя {user_id}: {e}")
    except Exception as e:
        print(f"Ошибка при отправке статистики: {e}")
    finally:
        await db.close()


def setup_scheduler():

    scheduler.add_job(send_daily_survey, "cron", minute="*")

    scheduler.add_job(send_weekly_statistics, "cron", day_of_week="sun", hour=10)

    scheduler.start()
