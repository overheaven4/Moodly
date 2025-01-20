# Импорт библиотеки asyncio для работы с асинхронным программированием
import asyncio

# Импорт модуля logging для ведения логирования событий
import logging

# Импорт класса Bot и Dispatcher из библиотеки aiogram
from aiogram import Bot, Dispatcher

# Импорт конфигурации с токеном
from config import TOKEN

# Импорт обработчиков (handlers) из файла app.handlers
from app.handlers import router

# Импорт функции async_main из файла app.database.models
####           from app.database.models import async_main


# Создание экземпляра бота с использованием токена из конфигурации
bot = Bot(token=TOKEN)

# Создание диспетчера для обработки обновлений
dp = Dispatcher()

# Асинхронная функция main, которая запускает бота
async def main():
    # Вызываем функцию async_main для инициализации базы данных
    ####    await async_main()
    
    # Добавляем роутер с обработчиками в диспетчер
    dp.include_router(router)
    
    # Начинаем обработку обновлений от Telegram API
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Настраиваем уровень логгирования на INFO
    logging.basicConfig(level=logging.INFO)
    
    # Запускаем основную функцию main в цикле событий asyncio
    try:
        asyncio.run(main())
    # Обрабатываем прерывание выполнения программы пользователем (Ctrl+C)
    except KeyboardInterrupt:
        print('Exit')
