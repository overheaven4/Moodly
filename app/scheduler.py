from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.bot import bot

scheduler = AsyncIOScheduler()


async def send_daily_survey():
    # Здесь будет логика для получения пользователей из БД
    user_id = 123456789  # Пример ID
    await bot.send_message(
        user_id, "Ваш ежедневный опрос: Как вы себя чувствуете сегодня?"
    )


def setup_scheduler():
    scheduler.add_job(
        send_daily_survey, "cron", hour=9
    )  # Отправка каждый день в 9 утра
    scheduler.start()
