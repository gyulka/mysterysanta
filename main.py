from collections import defaultdict
import random
import sqlite3
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

import config

bot = Bot(token=config.Token)
dp = Dispatcher(bot)

last = defaultdict(int)


def db_init():
    return sqlite3.connect('db.db')


@dp.message_handler(commands=['start'])
async def start_msg(message: types.Message):
    id = message.from_user.id
    con = db_init()
    if con.execute('select id from users where id=?', (id,)).fetchone() is None:
        con.execute('insert into users(id,menu) values(?,?)', (id, 1))
        con.commit()
    else:
        con.execute('update users set menu=1 where id=?', (id,))
        con.commit()
    await message.answer('Как тебя зовут?')


@dp.message_handler(commands=['generate'])
async def generate(message: types.Message):
    id = message.from_user.id
    con = db_init()
    lis = [(id, name)
           for name, id in con.execute('select name,id from users where name <> ""').fetchall()]
    lis1 = lis.copy()
    random.shuffle(lis1)
    flag = False
    for i in range(len(lis)):
        flag = lis[i][0] == lis1[i][0] or flag or last[lis[i][0]] == lis1[i][0]
    while flag:
        flag = False
        random.shuffle(lis1)
        for i in range(len(lis)):
            flag = lis[i][0] == lis1[i][0] or flag or last[lis[i][0]] == lis1[i][0]
    for i in range(len(lis)):
        await bot.send_message(lis[i][0], f'Завтра ты даришь: {lis1[i][1]}!')
        last[lis[i][0]] = lis1[i][0]



@dp.message_handler()
async def msg_handler(message: types.Message):
    id = message.from_user.id
    con = db_init()
    menu = con.execute('select menu from users where id=?', (id,)).fetchone()[0]
    if menu == 1:
        name = message.text
        con.execute('update users set name=?, menu=0 where id=?', (name[0].upper() + name[1:], id))
        con.commit()


if __name__ == '__main__':
    print('hello!')
    executor.start_polling(dp)
