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

# Definisce uno stato per la gestione del menu
class Menu(StatesGroup):
    main = State()

# Definisce una funzione per la gestione del comando /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Crea i pulsanti
    buttons = [types.InlineKeyboardButton(text="Pulsante 1", callback_data= 1 ),
               types.InlineKeyboardButton(text="Pulsante 2", callback_data= 2 ),
               types.InlineKeyboardButton(text="Pulsante 3", callback_data= 3 )]
    
    # Crea la markup della tastiera
    keyboard_markup = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
    # Invia il messaggio di benvenuto con i pulsanti
    await message.reply("Benvenuto! Seleziona una delle opzioni seguenti:", reply_markup=keyboard_markup)
    # Passa allo stato del menu principale
    await Menu.main.set()

# Definisce una funzione per la gestione dei pulsanti
@dp.message_handler(state=Menu.main)
async def process_menu_button(message: types.Message, state: FSMContext):
    # Ottiene il testo del pulsante selezionato
    button_text = message.text
    # Controlla quale pulsante è stato selezionato e invia una risposta di conseguenza
    if button_text == "Pulsante 1":
        await message.reply("Hai selezionato il pulsante 1")
    elif button_text == "Pulsante 2":
        await message.reply("Hai selezionato il pulsante 2")
    elif button_text == "Pulsante 3":
        await message.reply("Hai selezionato il pulsante 3")
    
    # Rimuove la tastiera dei pulsanti
    # keyboard_markup = ReplyKeyboardRemove()
    
    
    buttons = [types.InlineKeyboardButton(text="Pulsante 10", callback_data= 10 ),
               types.InlineKeyboardButton(text="Pulsante 20", callback_data= 20 ),
               types.InlineKeyboardButton(text="Pulsante 30", callback_data= 30 )]
    
    keyboard_markup = ReplyKeyboardMarkup(keyboard=[buttons], resize_keyboard=True)
    
    await message.reply("Seleziona un'altra opzione:", reply_markup=keyboard_markup)
    # Torna allo stato del menu principale
    await Menu.main.set()

if __name__ == '__main__':
    # Avvia il bot
    try:
        logging.info("Starting bot")
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
