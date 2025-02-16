from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot import bot
from app.database import get_database_connection
from app.handlers.survey import (
    BUTTON_TEXTS, 
    crat, 
    delta, 
    a, 
    WEEKDAYS,
)
scheduler = AsyncIOScheduler()


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
                    user_id, "Самое время пройти ежедневный опрос!\nИспользуйте команду /survey",
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
            user_id = user["id"]
            results = await db.fetch(
                """
                SELECT answer, created_at FROM survey_results
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '7 days'
                ORDER BY created_at
                """,
                user_id,
            )

            stats = "\n".join(
                [
                    f"{(row[crat] + delta).strftime(f'{WEEKDAYS[(row[crat] + delta).strftime(a)]} %d.%m, %H:%M')} - {BUTTON_TEXTS[row['answer']]}"
                    for row in results
                ]
            )
            average_mood = sum(row["answer"] for row in results) / len(results)
            await bot.send_message(
                user_id,
                f"Ваша статистика за последнюю неделю:\n{stats}\n\nСреднее настроение: {BUTTON_TEXTS[round(average_mood)]}",
            )
    except Exception as e:
        print(f"Ошибка при отправке статистики: {e}")
    finally:
        await db.close()


def setup_scheduler():
    scheduler.add_job(send_daily_survey, "cron", minute="*") 

    scheduler.add_job(
        send_weekly_statistics, "cron", day_of_week="sun", hour=10
    )

    scheduler.start()
