import sqlite3

from aiogram.types import message

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

async def db_table_val(tg_id: int, time: str):
	cursor.execute('INSERT INTO new_db (tg_id, time) VALUES (?, ?)', (tg_id, time))
	conn.commit()