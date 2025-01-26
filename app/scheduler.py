from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot import bot
from app.database import get_database_connection
from app.handlers.survey import BUTTON_TEXTS  # Импортируем словарь с текстами кнопок

scheduler = AsyncIOScheduler()


async def send_daily_survey():

    db = await get_database_connection()
    try:
        # Получаем всех пользователей и их время уведомлений
        users = await db.fetch("SELECT id, notification_time FROM users")
        for user in users:
            user_id = user["id"]
            notification_time = user["notification_time"]

            # Проверяем, что текущее время совпадает с временем уведомления
            now = datetime.now().time()
            if (
                now.hour == notification_time.hour
                and now.minute == notification_time.minute
            ):
                await bot.send_message(
                    user_id, "Самое время пройти ежедневный опрос!\nИспользуйте команду /survey",
                )
    except Exception as e:
        print(f"Ошибка при отправке ежедневного опроса: {e}")
    finally:
        await db.close()


async def send_weekly_statistics():

    db = await get_database_connection()
    try:
        # Получаем всех пользователей
        users = await db.fetch("SELECT id FROM users")
        for user in users:
            user_id = user["id"]
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
                average_mood = sum(row["answer"] for row in results) / len(results)
                await bot.send_message(
                    user_id,
                    f"Ваша статистика за последнюю неделю:\n{stats}\n\nСреднее настроение: {BUTTON_TEXTS[round(average_mood)]}",
                )
            else:
                await bot.send_message(
                    user_id, "У вас нет записей за последнюю неделю."
                )
    except Exception as e:
        print(f"Ошибка при отправке статистики: {e}")
    finally:
        await db.close()


def setup_scheduler():
    # Ежедневный опрос (проверка каждую минуту)
    scheduler.add_job(send_daily_survey, "cron", minute="*")  # Проверка каждую минуту

    # Еженедельная статистика
    scheduler.add_job(
        send_weekly_statistics, "cron", day_of_week="sun", hour=10
    )  # Отправка каждое воскресенье в 10 утра

    scheduler.start()
