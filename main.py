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
        InlineKeyboardButton('Ext Tree', callback_data='ext_tree'),
        InlineKeyboardButton('Sub Ghz Chart', callback_data='subghz_chart'),

    )
    return keyboard


async def send_file(filename, filedata, user_id):
    with open(f"files/{filename}", 'w') as file:
      file.write(filedata)
      # Invia il file come documento
    with open(f"files/{filename}", 'rb') as file:
      return await bot.send_document(user_id, file)




# Comando di start bash
@dp.message_handler(commands=['abash'])
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



@dp.message_handler(commands=['file_decoder'])
async def send_ext_list(message: types.Message):

    path_ext = "/ext"
    flipper = None
    try:
        flipper = PyFlipper(com="/dev/ttyACM0")
    except:
        await message.reply("Flipper non connesso")
        return None

    ext_list = flipper.storage.list(path=path_ext)
    #await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text=f"Ext Tree: {ext_list}")


    keyboard = []
    for folder in ext_list['dirs']:
        keyboard.append([InlineKeyboardButton(folder, callback_data=f"&X7_{path_ext}/{folder}")])

    for filee in ext_list['files']:
        keyboard.append([InlineKeyboardButton(filee['name'], callback_data=f"&X8_{path_ext}/{filee['name']}")])

    inlinieKayboard =  InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.reply("Ciao! Premi il pulsante qui sotto per continuare:", reply_markup=inlinieKayboard)


# CALLBACK PER CARTELLE
@dp.callback_query_handler(lambda query: query.data.startswith('&X7_'))
async def button_click(query: types.CallbackQuery):
    # Estrai il nome della cartella o del file dal callback_data
    folder_or_file_name = query.data[4:]  # Rimuovi il prefisso 'ext_'

    #await query.answer(f'Folder: {folder_or_file_name}')

    path_ext = folder_or_file_name
    flipper = None
    try:
        flipper = PyFlipper(com="/dev/ttyACM0")
    except:
        await bot.edit_message_text(chat_id=query.from_user.id,message_id=mess_response, text="Flipper non connesso")
        return None

    ext_list = flipper.storage.list(path=path_ext)
    #await bot.edit_message_text(chat_id=query.from_user.id,message_id=mess_response, text=f"Ext Tree: {ext_list}")


    keyboard = []
    oldpath = path_ext[:path_ext.rfind("/")]
    keyboard.append([InlineKeyboardButton("../", callback_data=f"&X7_{oldpath}")])
    for folder in ext_list['dirs']:
        keyboard.append([InlineKeyboardButton(folder, callback_data=f"&X7_{path_ext}/{folder}")])

    for filee in ext_list['files']:
        keyboard.append([InlineKeyboardButton(filee['name'], callback_data=f"&X8_{path_ext}/{filee['name']}")])

    inlinieKayboard =  InlineKeyboardMarkup(inline_keyboard=keyboard)

    chat_id = query.message.chat.id
    message_id = query.message.message_id

    await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
      text=f'Folder: {folder_or_file_name}', reply_markup=inlinieKayboard)

def converti_in_esadecimale(stringa):
    nuova_stringa = ""
    for i in range(0, len(stringa), 4):
        segmento = hex(int(stringa[i:i+4]))
        nuova_stringa += segmento + " "
    return nuova_stringa.strip()


# CALLBACK PER FILE
@dp.callback_query_handler(lambda query: query.data.startswith('&X8_'))
async def button_click(query: types.CallbackQuery):
    # Estrai il nome della cartella o del file dal callback_data
    folder_or_file_name = query.data[4:]  # Rimuovi il prefisso 'ext_'

    flipper = None
    try:
      flipper = PyFlipper(com="/dev/ttyACM0")
    except:
      await bot.edit_message_text(chat_id=query.from_user.id,message_id=mess_response, text="Flipper non connesso")
      return None
    plain_text = flipper.storage.read(file=folder_or_file_name)

    chat_id = query.message.chat.id
    msg = await send_file(folder_or_file_name[folder_or_file_name.rfind("/")+1:], plain_text, query.from_user.id);

    await query.answer(f'File: {folder_or_file_name}')
    data_values = plain_text[plain_text.find("\nRAW_Data: "):].replace("\nRAW_Data: "," ")
    data_values = [int(value) for value in data_values.split()]

    await invia_grafico(msg, data_values, "Dati totali")


    # Estraggo i dadi tra i due picchi minimi

    index_min_start = 0
    index_min_end = 0
    minore = 0
    soglia_inizio = 5000

                #Calcolo la fine
    for i in range(0, len(data_values)):
      if data_values[i] < minore:
        index_min_end = i
        minore = data_values[i]

    data_values = data_values[: index_min_end]

                #Calcolo l'inizio


    for i in range(0, len(data_values)):
      if data_values[i] > soglia_inizio:
        index_min_start = i

    data_values = data_values[index_min_start+1: ]



    await invia_grafico(msg, data_values, "Dati ridotti tra i 2 min")

                # Separo i dati in valori positivi e negativi
    valori_positivi = [x for x in data_values if x > 0]
    valori_negativi = [x for x in data_values if x < 0]

                # Calcolo la media dei valori positivi
    media_positivi = sum(valori_positivi) / len(valori_positivi) if valori_positivi else 0

                # Calcolo la media dei valori negativi
    media_negativi = sum(valori_negativi) / len(valori_negativi) if valori_negativi else 0

                # Ora puoi stampare o utilizzare queste medie come desideri
    print(f"Media dei valori positivi: {media_positivi}")
    print(f"Media dei valori negativi: {media_negativi}")

    data_filtrati = []


    for valore in data_values:
      if valore > media_positivi:
        data_filtrati.append(1)
      if valore < media_negativi and valore > -2000:
        data_filtrati.append(0)



    await invia_grafico(msg, data_filtrati, "Dati Binario")
    binario = ''.join(map(str, data_filtrati))

    hex_msg = converti_in_esadecimale(binario)



    await msg.reply(f"Decode terminato. \nMessaggio in hex: 1n{hex_msg}")



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



async def invia_grafico(data_msg, data_values, msg):
# Crea il grafico solo con i valori compresi fra i 2 picchi
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
        await data_msg.reply_photo(photo=buffer, caption=f'{msg}')
    except Exception as e:
        print(f"Errore nell'invio dell'immagine: {e}")

      # Chiudi la figura di Matplotlib
    plt.close()


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
        msg  = await bot.send_message(chat_id=callback_query.from_user.id, text ="Reading Sub-GHz from file")
        hex_msg = ""
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
        hex_msg = ""
        msg  = await bot.send_message(chat_id=callback_query.from_user.id, text ="Listener Sub-GHz avviato.")
        # Specifica la frequenza Sub-GHz desiderata (ad esempio, 433920000)
        subghz_frequency = 433920000
        # Avvia il listener
        #flipper.subghz.rx(frequency=subghz_frequency, raw=True)
        # Inizia a ricevere dati per un certo periodo di tempo (ad esempio, 5 secondi)
        timeout = 3
        start_time = time.time()

        #while time.time() - start_time < timeout:
        data = flipper.subghz.rx(frequency=subghz_frequency, raw=True, timeout= timeout)

        if data:
            with open('RAW_DATA_RECORDED.txt', 'w') as file:
                file.write(data)

            # Invia il file come documento
            with open('RAW_DATA_RECORDED.txt', 'rb') as file:
                data_msg = await bot.send_document(callback_query.from_user.id, file)

            # Invia i dati ricevuti come messaggio Telegram
            #for data_str in data.replace("Listening at 433919830. Press CTRL+C to stop"," ").replace(">:","").split("\r\n\n"):
            for data_str in [data.replace("Listening at 433919830. Press CTRL+C to stop"," ").replace(">:"," ").replace("\r\n\n", " ")]:
                data_values = []
                try:
                    data_values = [int(value) for value in data_str.split()]
                except:
                    await bot.edit_message_text(chat_id=callback_query.from_user.id,message_id=mess_response, text=f"Errore con i dati recuperati {data_str}")
                    return None
                await invia_grafico(data_msg, data_values, "Dati totali")


                # Estraggo i dadi tra i due picchi minimi

                index_min_start = 0
                index_min_end = 0
                minore = 0
                soglia_inizio = 5000

                #Calcolo la fine
                for i in range(0, len(data_values)):
                  if data_values[i] < minore:
                    index_min_end = i
                    minore = data_values[i]

                data_values = data_values[: index_min_end]

                #Calcolo l'inizio


                for i in range(0, len(data_values)):
                  if data_values[i] > soglia_inizio:
                    index_min_start = i

                data_values = data_values[index_min_start+1: ]



                await invia_grafico(data_msg, data_values, "Dati ridotti tra i 2 min")

                # Separo i dati in valori positivi e negativi
                valori_positivi = [x for x in data_values if x > 0]
                valori_negativi = [x for x in data_values if x < 0]

                # Calcolo la media dei valori positivi
                media_positivi = sum(valori_positivi) / len(valori_positivi) if valori_positivi else 0

                # Calcolo la media dei valori negativi
                media_negativi = sum(valori_negativi) / len(valori_negativi) if valori_negativi else 0

                # Ora puoi stampare o utilizzare queste medie come desideri
                print(f"Media dei valori positivi: {media_positivi}")
                print(f"Media dei valori negativi: {media_negativi}")

                data_filtrati = []


                for valore in data_values:
                    if valore > media_positivi:
                        data_filtrati.append(1)
                    if valore < media_negativi and valore > -2000:
                        data_filtrati.append(0)



                await invia_grafico(data_msg, data_filtrati, "Dati Binario")
                binario = ''.join(map(str, data_filtrati))


                hex_msg = converti_in_esadecimale(binario)



        await msg.reply(f"Listener Sub-GHz terminato. \nMessaggio in hex: 1n{hex_msg}")





if __name__ == '__main__':
    # Avvia il bot
    try:
        logging.info("Starting bot")
        executor.start_polling(dp)
    except Exception as e:
        logging.exception(e)
