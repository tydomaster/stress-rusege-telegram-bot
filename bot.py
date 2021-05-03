import telebot
from telebot import types
from random import randint
from time import sleep
from functools import wraps
from datetime import datetime
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

ids = []
link = {}
global timer

# algo
def algo():
    n = open("udars.txt", "r", encoding="utf-8")
    t = n.readlines()
    b = []
    ok = 1
    for i in t:
        if ok == 0:
            ok = 1
            continue
        temp = i.split("\n")
        b.append(temp[0])
        ok = 0

    for i in range(len(b)):
        s = b[i]
        for j in range(len(s)):
            if s[j] == s[j].upper():
                link[s.lower()] = s
                break

# algo
algo()

bot = telebot.TeleBot('1639467970:AAFaZC3aT_aJRlhEsULrDoVfjUx3EypiU_Y')
@bot.message_handler(commands=['start'])
def get_text_messages(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Привет', 'Пока')
    bot.reply_to(message, 'ща заботаем нах')
    ids.append(message.chat.id)

@bot.message_handler(content_types=["text"])
def any_msg(message):
    ind = randint(0, len(link) - 1)
    to_send = 'поставь ударение в слове '
    c = 0
    s = ""
    for j in link.keys():
        if c == ind:
            s = j
            break
        c += 1
    to_send += s
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(len(s)):
        if s[i].lower() == 'а' or s[i].lower() == 'о' or s[i].lower() == 'е' or s[i].lower() == 'ё' or s[i].lower() == 'у' or s[i].lower() == 'ы' or s[i].lower() == 'э' or s[i].lower() == 'я' or s[i].lower() == 'и' or s[i].lower() == 'ю':
            new = s[:i] + s[i].upper() + s[i + 1:len(s)]
            data = "bad"
            if new == link[s]:
                data = "good"
            callback_button = types.InlineKeyboardButton(text=new, callback_data=data + new)
            buttons.append(callback_button)


    for i in range(len(buttons)):
        keyboard.add(buttons[i])
    bot.send_message(message.chat.id, to_send, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data[:4] == "good":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="правильно! ответ: " + call.data[4:])
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="неправильно... ответ был: " + call.data[3:])




def mult_threading(func):
    """Декоратор для запуска функции в отдельном потоке"""

    @wraps(func)
    def wrapper(*args_, **kwargs_):
        import threading
        func_thread = threading.Thread(target=func,
                                       args=tuple(args_),
                                       kwargs=kwargs_)
        func_thread.start()
        return func_thread

    return wrapper

#  Сразу делаем функцию многопоточной
@mult_threading
def test():
    while 1:
        sleep(900)

        if (datetime.now().hour >= 23 or datetime.now().hour <= 9):
            continue

        for i in range(len(ids)):
            bot.send_message(chat_id=ids[i], text="привет! для тебя есть новое задание! если хочешь получить, просто напиши что-нибудь")


#  ==Проверяем работу==
#  Стартуем нашу долгоиграющую функцию
test()

#  Занимаемся очень важными делами
bot.polling(none_stop=True, interval=0)

