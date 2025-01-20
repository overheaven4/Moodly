from aiogram.types import (
    ReplyKeyboardMarkup,  # Класс для создания обычной клавиатуры
    KeyboardButton,        # Класс для создания кнопки на обычной клавиатуре
    InlineKeyboardMarkup,  # Класс для создания встроенной клавиатуры
    InlineKeyboardButton   # Класс для создания кнопки на встроенной клавиатуре
)
from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,  # Утилита для упрощения создания обычной клавиатуры
    InlineKeyboardBuilder  # Утилита для упрощения создания встроенной клавиатуры
)


async def new_kb():
    time = '11:05' #переменная будет подсасываться из дб вот в таком формате. такой формат у нее чтобы удобно потом вставлять в шедулер
    hour, minute = time.split(':') #разделяется, чтобы сделать 2 отдельные кнопки на часы и минуты
    kb_digit = InlineKeyboardBuilder()
    kb_digit.add(InlineKeyboardButton(text='-', callback_data='minus')) #(коллбек нерабочий)
    kb_digit.add(InlineKeyboardButton(text = minute, callback_data='---')) #здесь в пример идут минуты
    kb_digit.add(InlineKeyboardButton(text="+", callback_data='plus')) #(коллбек нерабочий)
    return kb_digit.adjust(3).as_markup()