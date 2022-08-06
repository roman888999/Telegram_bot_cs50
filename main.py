from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from datetime import datetime
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

loop = asyncio.get_event_loop()

bot = Bot(token=TOKEN)

provider_name = None
cid = None
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
conn = sqlite3.connect('db.db', check_same_thread=False)
cursor = conn.cursor()
now = datetime.now()


def db_table_val(date: int, provider_name: str, user_id: int, rating: int):
    cursor.execute(
        'INSERT INTO providers (date, provider_name, user_id, rating) VALUES (?, ?, ?, ?)',
        (now, provider_name, user_id, rating))
    conn.commit()

def providers_keyboard():
    btn_INTC = KeyboardButton('/INTC-Городок')
    btn_Gazik = KeyboardButton('/Gaziknet')
    btn_Kiyvstar = KeyboardButton('/Kyivstar')
    btn_lifecell = KeyboardButton('/lifecell')
    kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
    return kb_client.add(btn_INTC).add(btn_Gazik).add(btn_Kiyvstar).add(btn_lifecell)

def providers_rating_keyboard():
    b1 = InlineKeyboardButton(text="1", callback_data="1")
    b2 = InlineKeyboardButton(text="2", callback_data="2")
    b3 = InlineKeyboardButton(text="3", callback_data="3")
    b4 = InlineKeyboardButton(text="4", callback_data="4")
    b5 = InlineKeyboardButton(text="5", callback_data="5")
    kb_client = InlineKeyboardMarkup()
    return kb_client.row(b1, b2, b3, b4, b5)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id,
                            'Виберіть провайдера для оцінювання',
                            reply_markup=providers_keyboard())
        answer = message.text
        print("answer:", answer)


    except:
        await message.replay('Почніть чат з ботом')

@dp.message_handler(commands=['Gaziknet', 'INTC-Городок', 'Kyivstar', 'lifecell'])
async def raiting(message: types.Message):
    global provider_name
    global cid
    cid = message.from_user.id
    provider_name = message.text
    print("provider_name", provider_name)
    await bot.send_message(message.from_user.id,'Виберіть оцінку по 5 бальній шкалі :',reply_markup=providers_rating_keyboard())
    print("message.text:", message.text)

@dp.callback_query_handler()
async def process_callback_name(callback_query: types.CallbackQuery):

    db_table_val(date=now,
                     provider_name=provider_name,
                     user_id=cid,
                     rating=callback_query.data)
    user = conn.execute("SELECT AVG(rating)  FROM providers  WHERE provider_name =:provider_name",{"provider_name": provider_name} ).fetchone()
    raitingg = "%.2f" % user
    await bot.send_message(cid, f"Рейтинг вашого провайдера  : {raitingg}")


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)