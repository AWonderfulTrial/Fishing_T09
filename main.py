import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
import sqlite3


from config import BOT_TOKEN

dp = Dispatcher()
logger = logging.getLogger(__name__)

user_data = {}
k = 0
conn = sqlite3.connect('fishing.db', check_same_thread=False)
cursor = conn.cursor()

fish = ["fish_1", "fish_2", "fish_3"]

def setup_db():
    cursor.execute('CREATE TABLE IF NOT EXISTS Users (user_id STRING, last_location STRING)')
    conn.commit()
    cursor.execute('CREATE TABLE IF NOT EXISTS Users_inventory (user_id STRING, fish_1 INTEGER, fish_2 INTEGER, fish_3 INTEGER)')
    conn.commit()

@dp.message(CommandStart())
async def start(message: Message):
    global k
    if k == 0:
        user_id = message.from_user.id
        s = cursor.execute(f'SELECT * FROM Users WHERE user_id = {user_id}').fetchall()
        if len(s) == 0:
            cursor.execute(f'INSERT INTO Users (user_id, last_location) VALUES ({user_id}, NULL)')
            cursor.execute(f'INSERT INTO Users_inventory (user_id, fish_1, fish_2, fish_3) VALUES ({user_id}, 0, 0, 0)')
        k += 1
        await cmd_menu_start(message)
    elif k != 0:
        await cmd_menu_start(message)

async def cmd_menu_start(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'menu_start' WHERE user_id = {user_id}")
    conn.commit()
    reply_keyboard = [[KeyboardButton(text='🎣Рыбалка🎣'),
                       KeyboardButton(text='🛒Магазин🛒')],
                      [KeyboardButton(text='🎒Инвентарь🎒'),
                       KeyboardButton(text='🧿Коллекция🧿')],
                      [KeyboardButton(text='⚙Настройки⚙'),
                       KeyboardButton(text='📚Гайд📚')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Добро пожаловать на рыбалку!', reply_markup=kb)



async def cmd_fishing(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'fishing' WHERE user_id = {user_id}")
    conn.commit()
    reply_keyboard = [[]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer("test", reply_markup=kb)
'''
    await asyncio.sleep(2)
    r = random.choice(fish)
    f = cursor.execute(f"SELECT {r} FROM Users_inventory WHERE user_id = {user_id}").fetchone()[0]
    f += 1
    cursor.execute(f"UPDATE Users_inventory SET {r} = {f} WHERE user_id = {user_id}")
    conn.commit()
'''
async def cmd_shop(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'shop' WHERE user_id = {user_id}")
    conn.commit()
    await message.answer("test1", reply_markup=kb)

async def cmd_inventory(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'inventory' WHERE user_id = {user_id}")
    conn.commit()
    await message.answer("test2", reply_markup=kb)

async def cmd_collections(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'collections' WHERE user_id = {user_id}")
    conn.commit()
    await message.answer("test3", reply_markup=kb)

async def cmd_settings(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'settings' WHERE user_id = {user_id}")
    conn.commit()
    reply_keyboard = [[KeyboardButton(text='❌УДАЛИТЬ ДАННЫЕ❌')],
                        [KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Выберите опцию:', reply_markup=kb)

async def cmd_reset_request(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'reset_request' WHERE user_id = {user_id}")
    conn.commit()
    reply_keyboard = [[KeyboardButton(text='✅ДА✅'),
                        KeyboardButton(text='⏪ВЕРНУТЬСЯ⏪')]]
    kb = ReplyKeyboardMarkup(keyboard=reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    await message.answer('Вы точно хотите удалить данные?', reply_markup=kb)

async def cmd_reset_request_approved(message: Message):
    user_id = message.from_user.id
    cursor.execute(f'DELETE from Users WHERE user_id = {user_id}')
    conn.commit()
    await message.answer('Ваши данные были успешно удалены!', reply_markup=ReplyKeyboardRemove())

async def cmd_guide(message: Message):
    user_id = message.from_user.id
    cursor.execute(f"UPDATE Users SET last_location = 'guide' WHERE user_id = {user_id}")
    conn.commit()
    await message.answer("test4", reply_markup=kb)







@dp.message()
async def handle_buttons(message: Message):
    user_id = message.from_user.id
    location = cursor.execute(f'SELECT last_location from Users WHERE user_id = {user_id}').fetchone()
    if location[0] == 'menu_start':
        if message.text == '🎣Рыбалка🎣':
            await cmd_fishing(message)
        elif message.text == '🛒Магазин🛒':
            await cmd_shop(message)
        elif message.text == '🎒Инвентарь🎒':
            await cmd_inventory(message)
        elif message.text == '🧿Коллекция🧿':
            await cmd_collections(message)
        elif message.text == '⚙Настройки⚙':
            await cmd_settings(message)
        elif message.text == '📚Гайд📚':
            await cmd_guide(message)
    elif location[0] == 'fishing':
        pass
    elif location[0] == 'shop':
        pass
    elif location[0] == 'inventory': #make a new location
        pass
    elif location[0] == 'collections': #make a new location
        pass
    elif location[0] == 'settings':
        if message.text == '❌УДАЛИТЬ ДАННЫЕ❌':
            await cmd_reset_request(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'reset_request':
        if message.text == '✅ДА✅':
            await cmd_reset_request_approved(message)
        elif message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    elif location[0] == 'guide': #make a new location
        if message.text == '⏪ВЕРНУТЬСЯ⏪':
            await cmd_menu_start(message)
    else:
        await message.answer('Выберите действие')


async def main():
    bot = Bot(token=BOT_TOKEN)
    setup_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
    )
    asyncio.run(main())