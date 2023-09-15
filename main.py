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

response_msg = {}
request_msg = {}

# Funzione per creare il layout dei pulsanti inline
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('App List', callback_data='appList'),
        #:InlineKeyboardButton('Power OFF', callback_data='powerOff'),
        #InlineKeyboardButton('Reboot', callback_data='reboot'),
        #InlineKeyboardButton('Ext Tree', callback_data='ext_tree'),
        InlineKeyboardButton('Sub Ghz Chart', callback_data='subghz_chart'),
        
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
    global request_msg  # Dichiarare request_msg come variabile globale
    global response_msg  # Dichiarare request_msg come variabile globale

    if message.from_user.id not in response_msg:
        ms = await message.reply("Ciao! Premi il pulsante qui sotto per continuare:", reply_markup=get_inline_keyboard())
        #request_msg[message.from_user.id] = ms.message_id
    else :
        del response_msg[message.from_user.id]
        await message.reply("Ciao! Premi il pulsante qui sotto per continuare:", reply_markup=get_inline_keyboard())
        #await bot.edit_message_text(chat_id=message.from_user.id,message_id=request_msg,
        #     text="Ciao! Premi il pulsante qui sotto per continuare:",  reply_markup=get_inline_keyboard())


    

# Gestione del callback dei pulsanti inline
@dp.callback_query_handler(lambda c: c.data in ['appList', 'reboot', 'powerOff', 'ext_tree', 'subghz_chart'])
async def process_callback_buttons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    
    if callback_query.from_user.id not in response_msg:
        ms = await bot.send_message(callback_query.from_user.id, f"Doing...")
        response_msg[callback_query.from_user.id] = ms.message_id
    
    mess_response = response_msg[callback_query.from_user.id]


    flipper = None
    try:
        flipper = PyFlipper(com="/dev/ttyACM0")
    except:
        await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text="Flipper non connesso")
        return None

    if 'appList' == callback_query.data:
        apps = flipper.loader.list()
        #flipper.loader.open(app_name="Clock")
        await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text= f"App List: {apps}")
    elif 'powerOff' == callback_query.data:
        await flipper.power.off()
        await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text=f"Hai premuto il pulsante {callback_query.data}")
    elif 'reboot' == callback_query.data:
        await flipper.power.reboot()
        await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text=f"Rebooting...")
    elif 'ext_tree' == callback_query.data:
        #ext_tree = flipper.storage.tree(path="/ext")
        ext_list = flipper.storage.list(path="/ext")
        await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text=f"Ext Tree: {ext_list}")
    elif 'subghz_chart' == callback_query.data:
        msg  = await bot.send_message(chat_id=callback_query.from_user.id, text ="Listener Sub-GHz avviato.")
        # Specifica la frequenza Sub-GHz desiderata (ad esempio, 433920000)
        subghz_frequency = 433920000
        # Avvia il listener
        #flipper.subghz.rx(frequency=subghz_frequency, raw=True)
        # Inizia a ricevere dati per un certo periodo di tempo (ad esempio, 5 secondi)
        timeout = 1
        start_time = time.time()

        #while time.time() - start_time < timeout:
        data = flipper.subghz.rx(frequency=subghz_frequency, raw=True, timeout= timeout)
        
        if data:
            # Invia i dati ricevuti come messaggio Telegram
            #for data_str in data.replace("Listening at 433919830. Press CTRL+C to stop"," ").replace(">:","").split("\r\n\n"):
            for data_str in data.replace("Listening at 433919830. Press CTRL+C to stop"," ").replace(">:"," ").replace("\r\n\n", " "):
                data_values = [int(value) for value in data_str.split()]
                
                # Crea il grafico
                plt.figure(figsize=(10, 6))
                plt.plot(data_values)
                plt.title('Dati ricevuti dal Sub-GHz')
                plt.xlabel('Campione')
                plt.ylabel('Valore')
                plt.grid(True)
            

                # Salva il grafico in un buffer
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                try:
                    await msg.reply_photo(photo=buffer, caption='Grafico dei dati ricevuti dal Sub-GHz')
                except Exception as e:
                    print(f"Errore nell'invio dell'immagine: {e}")

                # Chiudi la figura di Matplotlib
                plt.close()

        await msg.reply("Listener Sub-GHz terminato.")
        


    

if __name__ == '__main__':
    # Avvia il bot
    try:
        logging.info("Starting bot")
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
