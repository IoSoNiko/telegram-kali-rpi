import sys
import logging
import aiogram.utils.markdown as md
from aiogram.utils import executor
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import ReplyKeyboardRemove

# Imposta il livello di registro su DEBUG
logging.basicConfig(level=logging.DEBUG)

with open('tokenFile', 'r') as f:
    BOT_TOKEN = f.read().strip()

# Crea un'istanza del bot
bot = Bot(token=BOT_TOKEN)

# Crea un'istanza del dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Funzione per creare il layout dei pulsanti inline
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Pulsante 1', callback_data='button1'),
        InlineKeyboardButton('Pulsante 2', callback_data='button2')
    )
    return keyboard

# Comando di start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Ciao! Premi il pulsante qui sotto per continuare:", reply_markup=get_inline_keyboard())

# Gestione del callback dei pulsanti inline
@dp.callback_query_handler(lambda c: c.data in ['button1', 'button2'])
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Hai premuto il pulsante {callback_query.data}")

    
    

if __name__ == '__main__':
    # Avvia il bot
    try:
        logging.info("Starting bot")
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
