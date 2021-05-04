import operator
import telebot
from telebot import types
from random import randint
from time import sleep
from functools import wraps
from datetime import datetime


class User:
    def __init__(self, id, correct, wrong, last_answer, first_name, last_name, skipped, used):
        self.id = id
        self.correct = correct
        self.wrong = wrong
        self.last_answer = last_answer
        self.first_name = first_name
        self.last_name = last_name
        self.skipped = skipped
        self.used = used

# сделать мапу для всех слов, каждому слову свой номер, так будет проще
# сделать нормально юзды
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
    n.close()


def start_prog():
    text = open("bd.txt", "r")
    for line in text:
        a = line.split()
        used_local = {}
        for i in range(6, len(a)):
            used_local[a[i]] = 1
        ids.append(User(int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4], a[5], int(a[6]), used_local))


start_prog()
algo()
# algo
bot = telebot.TeleBot('1639467970:AAFaZC3aT_aJRlhEsULrDoVfjUx3EypiU_Y')


def get_info():
    print("current users:")
    for i in range(len(ids)):
        print(i, ') ', ids[i].first_name, ' ', ids[i].last_name, ': correct: ', ids[i].correct, ', wrong: ',
              ids[i].wrong, ', last_ans = ', ids[i].last_answer, sep="")


def upd_b():
    file1 = open("bd.txt", "r")
    file2 = open("bd_backup.txt", "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open("bd.txt", "w")
    file1.truncate(0)
    for i in range(len(ids)):
        used_str = ""
        for j in ids[i].used.keys():
            used_str += str(j) + ' '
        file1.write(str(ids[i].id) + ' ' + str(ids[i].correct) + ' ' + str(ids[i].wrong) + ' ' + str(ids[i].last_answer) + ' ' + str(ids[i].first_name) + ' ' + str(ids[i].last_name) + ' ' + str(ids[i].skipped) + ' ' + used_str + '\n')
    file1.close()


def get_time():
    date = datetime.now()
    # print(date.month, date.day, date.hour, date.minute, date.second)
    ret = date.hour + date.day * 24 + date.month * 31
    return ret


def comparator(a):
    return a.correct


@bot.message_handler(commands=['start'])  # ответ на команду /start
def hello(message):
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.row('слово!', 'статы', 'топ')
    for i in range(len(ids)):
        if int(ids[i].id) == int(message.chat.id):
            bot.reply_to(message, f'мы уже здоровались!', reply_markup=keyboard)
            return
    bot.reply_to(message, f'привет! готов закидать тебя словами!', reply_markup=keyboard)
    ids.append(User(message.chat.id, 0, 0, get_time(), message.chat.first_name, message.chat.last_name, 0))


@bot.message_handler(content_types=["text"])  # ответ на любой текст
def any_msg(message):
    if message.text.lower() != 'слово!' and message.text.lower() != 'статы' and message.text.lower() != 'топ':
        print(message.from_user.first_name, message.from_user.last_name, "сказал", message.text)
        upd_b()
        bot.send_message(message.chat.id, "я, скорее всего, еще туповат, чтобы понять, что тут написано...")
        return
    if message.text.lower() == 'статы':
        ind = 0
        for i in range(len(ids)):
            if ids[i].id == message.chat.id:
                ind = i
                break
        bot.send_message(message.chat.id, "твои статы:\nправильных ответов: " + str(ids[ind].correct) + "\nнеправильных ответов: "+ str(ids[ind].wrong))
        return
    if message.text.lower() == 'топ':
        ids.sort(key=comparator, reverse=True)
        s = "текущий топ по количеству правильных ответов:\n"
        for i in range(len(ids)):
            s += str(i + 1) + ") " + str(ids[i].correct) + " "
            s += "- "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += '\n'
        bot.send_message(message.chat.id, s)
        return

    ind_ids = 0
    for j in range(len(ids)):
        if ids[j].id == message.chat.id:
            ind_ids = j
            break

    if len(ids[ind_ids].used) == 324:
        ids[ind_ids].used.clear()

    to_send = 'поставь ударение в слове '
    c = 0
    s = ""
    while 1:
        ind = randint(0, len(link) - 1)
        c = 0
        s = ""
        for j in link.keys():
            if c == ind:
                s = j
                break
            c += 1
        if s not in ids[ind_ids].used:
            break

    to_send += s
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for i in range(len(s)):
        if s[i].lower() == 'а' or s[i].lower() == 'о' or s[i].lower() == 'е' or s[i].lower() == 'ё' or s[
            i].lower() == 'у' or s[i].lower() == 'ы' or s[i].lower() == 'э' or s[i].lower() == 'я' or s[
            i].lower() == 'и' or s[i].lower() == 'ю':
            new = s[:i] + s[i].upper() + s[i + 1:len(s)]
            data = "bad"
            if new == link[s]:
                data = "good"
            callback_button = types.InlineKeyboardButton(text=new, callback_data=data + new)
            buttons.append(callback_button)

    for i in range(len(buttons)):
        keyboard.add(buttons[i])
    bot.send_message(message.chat.id, to_send, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)  # реакция на ответ на задачу
def callback_inline(call):
    if call.data[:4] == "good":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="правильно! ответ: " + link[call.data[4:].lower()])
        for i in range(len(ids)):
            if ids[i].id == call.message.chat.id:
                ids[i].correct += 1
                ids[i].last_answer = get_time()
                ids[i].skipped = 0
                ids[i].used[link[call.data[4:].lower()]] = 1
                upd_b()
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="неправильно... ответ был: " + link[call.data[3:].lower()])
        for i in range(len(ids)):
            if ids[i].id == call.message.chat.id:
                ids[i].wrong += 1
                ids[i].last_answer = get_time()
                ids[i].skipped = 0
                upd_b()


def multi_threading(func):  # Декоратор для запуска функции в отдельном потоке
    @wraps(func)
    def wrapper(*args_, **kwargs_):
        import threading
        func_thread = threading.Thread(target=func,
                                       args=tuple(args_),
                                       kwargs=kwargs_)
        func_thread.start()
        return func_thread

    return wrapper


@multi_threading
def test():  # предложение ответить на вопрос каждые N единиц времени
    while 1:
        sleep(7200)
        if datetime.now().hour >= 23 or datetime.now().hour <= 9:
            continue
        nowtime = get_time()
        for i in range(len(ids)):
            if nowtime - int(ids[i].last_answer) >= 1 and ids[i].skipped < 3:
                ids[i].skipped += 1
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! для тебя есть новое задание! если хочешь получить, нажми на кнопочку)")
            elif ids[i].skipped >= 3 and ids[i].skipped < 4 and nowtime - int(ids[i].last_answer) >= 5:
                ids[i].skipped += 1
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! давно тебя не было в уличных гонках! если хочешь получить вопросик, нажми на кнопочку)")
            elif ids[i].skipped >= 4 and ids[i].skipped < 5 and nowtime - int(ids[i].last_answer) >= 5:
                ids[i].skipped += 1
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! последний раз предлагаю тебе вспомнить про ударения на егэ!")


test()
bot.polling(none_stop=True, interval=0)
