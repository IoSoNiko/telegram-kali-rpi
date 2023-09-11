import sys
import logging
import subprocess
from aiogram import types
from aiogram.dispatcher.filters import Command
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
from pyflipper.pyflipper import PyFlipper



# Imposta il livello di registro su DEBUG
logging.basicConfig(level=logging.DEBUG)

with open('tokenFile', 'r') as f:
    BOT_TOKEN = f.read().strip()

# Crea un'istanza del bot
bot = Bot(token=BOT_TOKEN)

# Crea un'istanza del dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
flipper = PyFlipper(com="/dev/ttyACM0")


# Funzione per creare il layout dei pulsanti inline
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Storage Info', callback_data='infoStorage'),
        InlineKeyboardButton('Pulsante 2', callback_data='button2')
    )
    return keyboard

# Comando di start bash
@dp.message_handler(commands=['bash'])
async def on_bash_command(message: types.Message):
    # Verifica che l'utente che ha inviato il messaggio sia autorizzato a eseguire il comando
    if message.from_user.id not in [33033257, 1138794081]: # sostituisci questi numeri con gli ID degli utenti autorizzati
        return

    # Estrai il comando dalla stringa del messaggio
    command = message.text[len('/bash '):]

    # Esegui il comando sulla bash e cattura l'output
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        result = e.output

    # Invia l'output in chat
    await message.reply(result.decode())

# Comando di start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Ciao! Premi il pulsante qui sotto per continuare:", reply_markup=get_inline_keyboard())

# Gestione del callback dei pulsanti inline
@dp.callback_query_handler(lambda c: c.data in ['infoStorage', 'button2'])
async def process_callback_buttons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    

    if 'infoStorage' == callback_query.id:
        ext_info = flipper.storage.info(fs="/ext")
        await bot.send_message(callback_query.from_user.id, f"Info Storage: {ext_info}")
    else:
        await bot.send_message(callback_query.from_user.id, f"Hai premuto il pulsante {callback_query.data}")

    
    

if __name__ == '__main__':
    # Avvia il bot
    try:
        
        logging.info("Starting bot")
        executor.start_polling(dp)


    except Exception as e:
        logging.exception(e)
