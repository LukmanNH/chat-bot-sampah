import json 
import requests
import time
import urllib
import sqlite3
import sys

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def loadDB():
        conn = sqlite3.connect('Telegram-BOTpy')
        cur = conn.cursor()
        conn.text_factory = str
        cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
        (
        id INTEGER NOT NULL PRIMARY KEY UNIQUE, 
        firstname TEXT, 
        Nama TEXT,
        Alamat TEXT,
        Telp TEXT);'''
        )
        conn.commit()
        conn.close()

def checkUser(update, user_data):
    conn = sqlite3.connect('Telegram-BOTpy')
    cur = conn.cursor()
    conn.text_factory = str
    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?        
            ''', (update.message.from_user.id,)).fetchall())>0:
        c=cur.execute('''SELECT Nama FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Nama']=c[0]
        c=cur.execute('''SELECT Alamat FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Alamat']=c[0]
        c=cur.execute('''SELECT Telp FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Telp']=c[0]
        print('Past user')
    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname) VALUES (?, ?)''', \
        (update.message.from_user.id, update.message.from_user.first_name,))
        print('New user')
    conn.commit()
    conn.close()

def updateUser(category, text, update):
    conn = sqlite3.connect('Telegram-BOTpy')
    cur = conn.cursor()
    conn.text_factory = str
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.message.from_user.id,))
    conn.commit()
    conn.close()


reply_keyboard = [['Nama' , 'Telp'],
                  ['Alamat'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

def facts_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))
    return "\n".join(facts).join(['\n', '\n'])

def start(bot, update, user_data):
    update.message.reply_text(
        "Selamat datang di Pemanggil Tukang Sampah. Sampah menumpuk?. Tidak sempat membuangnya? panggil kami. Kami siap mengambil sampah di rumah Anda. "
        "\n\nIsi data diri Anda untuk memanggil tukang sampah kami ke rumah Anda."
        "\nKetik /start jika tombol di bawah tidak muncul"    
        ,
        reply_markup=markup)
    checkUser(update, user_data)
    return CHOOSING

def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Silakan ketikan {}mu :)  '.format(text.lower()))
    return TYPING_REPLY

def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    updateUser(category, text, update)
    del user_data['choice']

    update.message.reply_text("Data sudah masuk ke dalam database kami."
                              "{}".format(facts_to_str(user_data)), reply_markup=markup)
    return CHOOSING


def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("data sudah masuk ke dalam database gan"
                              "{}".format(facts_to_str(user_data)))
    update.message.reply_text("Mohon menunggu tukang sampah kami datang kesana \nTerima kasih")
    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("937899228:AAFDo4YAYcF51Fy06tlAFFK3hGpQcKUh460")
    print("Bot jalan gan")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],
        states={
            CHOOSING: [RegexHandler('^(Nama|Telp|Alamat)$',
                                    regular_choice,
                                    pass_user_data=True),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },
        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


    
if __name__ == '__main__':
    loadDB()
    main()

"""========================="""

# def get_url(url):
#     response = requests.get(url)
#     content = response.content.decode("utf8")
#     return content

# def get_json_from_url(url):
#     content = get_url(url)
#     js = json.loads(content)
#     return js

# def get_updates(offset=None):
#     url = URL + "getUpdates"
#     if offset:
#         url += "?offset={}".format(offset)
#     js = get_json_from_url(url)
#     return js


# def get_last_update_id(updates):
#     update_ids = []
#     for update in updates["result"]:
#         update_ids.append(int(update["update_id"]))
#     return max(update_ids)



# def handle_updates(updates):
#     cmd = {'/help' , '/gantialamat' , '/start' '/sampah' , '/hapusalamat' , '/alamat'}
#     for update in updates["result"]:
#         text = update["message"]["text"]
#         chat = update["message"]["chat"]["id"]
#         items = db.get_items(chat)
#         if text == ("/sampah"):
#             send_message("Ketik /alamat lalu masukan alamat rumah mu" , chat)
#         if text == ("/alamaaat"):
#             send_message("Silakan masukan alamat anda" , chat)
#             # else:
#             #     send_message("Masukan alamat yang valid" , chat)
#         elif text == ("/gantialamat"):
#             keyboard = build_keyboard(items)
#             send_message("Select an item to delete", chat, keyboard)
#         elif text == "/start":
#             send_message("Selamat datang di Pemanggil Tukang Sampah. Sampah menumpuk?. Tidak sempat membuangnya? panggil kami. Kami siap mengambil sampah di rumah Anda", chat)
#             send_message("Ketik /sampah untuk memanggil tukang sampah" , chat)
#             send_message("ketik /help untuk bantuan" , chat)
#         elif text == ("/"):
#             send_message("Command tidak di ketahui ketik /help untuk bantuan" , chat)
#         elif text == ("/help"):
#             send_message("/start untuk memulai chat bot ini \n/sampah untuk mulai memanggil tukang sampah.\n/gantialamat untuk mengganti alamat pengambilan sampah" , chat)
#         elif text in items:
#             db.delete_item(text, chat)
#             items = db.get_items(chat)
#             keyboard = build_keyboard(items)
#             send_message("Masukan alamat yang baru", chat, keyboard)
#         elif text == ("/done"):
#             send_message("ketik /sampah lagi untuk memanggil tukang sampah " ,chat)
#             continue
#         elif text != cmd:
#             send_message("Command tidak di ketahui ketik /help untuk bantuan" , chat)
#         # else:
#         #     send_message("Command tidak di ketahui ketik /help untuk bantuan" , chat)
#             # db.add_item(text , chat)
#             # items = db.get_items(chat)
#             # message = "\n".join(items)
#             # send_message(message + " Sudah di masukan ke dalam database"  , chat)
#             # send_message("Mohon untuk menunggu tukang sampah kami datang kesana" , chat)
#             # send_message("Terima Kasih \nKetik /done untuk menyudahi" , chat)

# def build_keyboard(items):
#     keyboard = [[item] for item in items]
#     reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
#     return json.dumps(reply_markup)

# def get_last_chat_id_and_text(updates):
#     num_updates = len(updates["result"])
#     last_update = num_updates - 1
#     text = updates["result"][last_update]["message"]["text"]
#     chat_id = updates["result"][last_update]["message"]["chat"]["id"]
#     return (text, chat_id)


# def send_message(text, chat_id, reply_markup=None):
#     text = urllib.parse.quote_plus(text)
#     url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
#     if reply_markup:
#         url += "&reply_markup={}".format(reply_markup)
#     get_url(url)


