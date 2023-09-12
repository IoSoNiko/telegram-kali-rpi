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
import time
import matplotlib.pyplot as plt
from io import BytesIO
import base64



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
        InlineKeyboardButton('App List', callback_data='appList'),
        InlineKeyboardButton('Power OFF', callback_data='powerOff'),
        InlineKeyboardButton('Reboot', callback_data='reboot'),
        InlineKeyboardButton('Ext Tree', callback_data='ext_tree'),
        
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
@dp.callback_query_handler(lambda c: c.data in ['appList', 'reboot', 'powerOff', 'ext_tree'])
async def process_callback_buttons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    flipper = PyFlipper(com="/dev/ttyACM0")

    if 'appList' == callback_query.data:
        apps = flipper.loader.list()
        #flipper.loader.open(app_name="Clock")
        await bot.send_message(callback_query.from_user.id, f"App List: {apps}")
    elif 'powerOff' == callback_query.data:
        await flipper.power.off()
        await bot.send_message(callback_query.from_user.id, f"Hai premuto il pulsante {callback_query.data}")
    elif 'reboot' == callback_query.data:
        await flipper.power.reboot()
        await bot.send_message(callback_query.from_user.id, f"Rebooting...")
    elif 'ext_tree' == callback_query.data:
        #ext_tree = flipper.storage.tree(path="/ext")
        ext_list = flipper.storage.list(path="/ext")

        await bot.send_message(callback_query.from_user.id, f"Ext Tree: {ext_list}")


#Get the storage /ext tree dict

    
@dp.message_handler(commands=['start_subghz_listener'])
async def start_subghz_listener(message: types.Message):
    # Verifica che l'utente abbia i permessi necessari per avviare il listener Sub-GHz
    if message.from_user.id not in [33033257, 1138794081]:  # Sostituisci questi numeri con gli ID degli utenti autorizzati
        return

    # Usa PyFlipper per avviare il listener Sub-GHz
    flipper = PyFlipper(com="/dev/ttyACM0")

    # Specifica la frequenza Sub-GHz desiderata (ad esempio, 433920000)
    subghz_frequency = 433920000

    # Avvia il listener
    flipper.subghz.rx(frequency=subghz_frequency, raw=True)

    # Inizia a ricevere dati per un certo periodo di tempo (ad esempio, 5 secondi)
    timeout = 5
    start_time = time.time()

    while time.time() - start_time < timeout:
        data = flipper.subghz.rx(frequency=subghz_frequency, raw=True)
        
        if data:
            # Invia i dati ricevuti come messaggio Telegram
            for data_str in data.replace("Listening at 433919830. Press CTRL+C to stop"," ").split("\r\n\n"):
                data_values = [int(value) for value in data_str.split()]
                x_values = range(len(data_values))
                plt.scatter(x_values, data_values, marker='.', s=10)  # Usiamo 'marker' per specificare il tipo di marcatore

                # Crea il grafico
                plt.figure(figsize=(10, 6))
                #plt.plot(data_values)
                plt.title('Dati ricevuti dal Sub-GHz')
                plt.xlabel('Campione')
                plt.ylabel('Valore')
                plt.grid(True)
            

                # Salva il grafico in un buffer
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                try:
                    await message.reply_photo(photo=buffer, caption='Grafico dei dati ricevuti dal Sub-GHz')
                except Exception as e:
                    print(f"Errore nell'invio dell'immagine: {e}")

                # Chiudi la figura di Matplotlib
                plt.close()
            
                #await message.reply(f"Dati ricevuti dal Sub-GHz: {d}")

    await message.reply("Listener Sub-GHz terminato.")
    

if __name__ == '__main__':
    # Avvia il bot
    try:
        logging.info("Starting bot")
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
