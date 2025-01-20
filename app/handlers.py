from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F

import app.keyboards as kb

from app.db.test import db_table_val

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('started')

@router.message(Command('reg'))
async def reg(message: Message):
    tg_id = message.from_user.id
    time = '11:06'
    await db_table_val(tg_id=tg_id, time=time)
    await message.answer('Зарегистрирован')

@router.message(Command('time'))
async def time(message: Message):
    await message.answer('циферка', reply_markup = await kb.new_kb())

@router.callback_query(F.data == 'minus')
async def minus(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_reply_markup('циферка', reply_markup = await kb.new_kb())

@router.callback_query(F.data == 'plus')
async def minus(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_reply_markup('циферка', reply_markup = await kb.new_kb())

@router.callback_query(F.data == '---')
async def nothing(callback: CallbackQuery):
    await callback.answer()






