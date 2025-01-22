import asyncio
import logging

from asyncpg import connect

from app.config import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL-запросы для создания таблиц
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    notification_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

CREATE_SURVEY_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS survey_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users (id),
    answer INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""


async def setup_database():

    conn = await connect(config.DATABASE_URL)
    try:
        await conn.execute(CREATE_USERS_TABLE)
        await conn.execute(CREATE_SURVEY_RESULTS_TABLE)
        logger.info("Таблицы созданы.")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
    finally:
        await conn.close()


async def get_database_connection():

    logger.info("Получение соединения с базой данных")
    conn = await connect(config.DATABASE_URL)
    return conn
