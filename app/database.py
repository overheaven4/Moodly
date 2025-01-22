import asyncio
from asyncpg import connect
from app.config import config

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    notification_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

"""


CREATE_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS survey_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    answer JSONB NOT NULL,
	created_at TIMESTAMP DEFAULT NOW()
);
"""


async def setup_database():
    conn = await connect(config.DATABASE_URL)
    try:
        await conn.execute(CREATE_USERS_TABLE)
        await conn.execute(CREATE_RESULTS_TABLE)
        print("Таблицы созданы.")
    finally:
        await conn.close()


async def get_database_connection():
    conn = await connect(config.DATABASE_URL)
    return conn
