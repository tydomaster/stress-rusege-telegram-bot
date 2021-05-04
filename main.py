import operator
import telebot
from telebot import types
from random import randint
from time import sleep
from functools import wraps
from datetime import datetime


class User:
    def __init__(self, id, correct, wrong, last_answer, first_name, last_name, skipped, top, used):
        self.id = id
        self.correct = correct
        self.wrong = wrong
        self.last_answer = last_answer
        self.first_name = first_name
        self.last_name = last_name
        self.skipped = skipped
        self.used = used
        self.top = top

# сделать мапу для всех слов, каждому слову свой номер, так будет проще
# сделать нормально юзды
words = []
ids = []
link = {}
global timer


# algo
def algo():
    n = open("udars.txt", "r", encoding="utf-8")
    t = n.readlines()
    ok = 1
    for i in t:
        if ok == 0:
            ok = 1
            continue
        temp = i.split("\n")
        words.append(temp[0])
        ok = 0
    for i in range(len(words)):
        s = words[i]
        for j in range(len(s)):
            if s[j] == s[j].upper():
                link[s.lower()] = s
                break
    for i in range(len(words)):
        words[i] = words[i].lower()
    n.close()

def start_prog():
    text = open("bd.txt", "r")
    for line in text:
        a = line.split()
        used_local = []
        for i in range(8, len(a)):
            used_local.append(int(a[i]))
        ids.append(User(int(a[0]), int(a[1]), int(a[2]), int(a[3]), a[4], a[5], int(a[6]), int(a[7]), used_local))


start_prog()
algo()
# algo
bot = telebot.TeleBot('1639467970:AAEXXyaLvwq1LIe9rOMjo0AzyhMlVKl-3Xc')


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
        for j in ids[i].used:
            used_str += str(j) + ' '
        file1.write(str(ids[i].id) + ' ' + str(ids[i].correct) + ' ' + str(ids[i].wrong) + ' ' + str(ids[i].last_answer) + ' ' + str(ids[i].first_name) + ' ' + str(ids[i].last_name) + ' ' + str(ids[i].skipped) + ' ' + str(ids[i].top) + ' ' + used_str + '\n')
    file1.close()


def get_time():
    date = datetime.now()
    # print(date.month, date.day, date.hour, date.minute, date.second)
    ret = date.hour + date.day * 24 + date.month * 31
    return ret


def comparator(a):
    return a.correct


def get_id(message_id):
    ind = -1
    for i in range(len(ids)):
        if ids[i].id == message_id:
            ind = i
            break
    return ind


#клавиатуры_start

keyboard_main = types.ReplyKeyboardMarkup(True, False)
keyboard_main.row('слово!', 'статы', 'топ', 'настройки')
keyboard_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_settings.row('настройки отображения в топе', 'выйти из настроек')

# отображение в топе
callback_buttons_top = types.InlineKeyboardMarkup()
callback_button_top1 = types.InlineKeyboardButton(text="да", callback_data="top_yes")
callback_button_top2 = types.InlineKeyboardButton(text="нет", callback_data="top_no")
callback_buttons_top.add(callback_button_top1)
callback_buttons_top.add(callback_button_top2)

#клавиатуры_end


@bot.message_handler(commands=['start'])  # ответ на команду /start
def start(message):
    ind = get_id(message.chat.id)
    if ind != -1:
        bot.reply_to(message, f'мы уже здоровались!', reply_markup=keyboard_main)
        return
    new_used = [0] * len(words)
    ids.append(User(message.chat.id, 0, 0, get_time(), message.chat.first_name, message.chat.last_name, 0, 0, new_used))
    bot.reply_to(message, f'привет! готов закидать тебя словами! советую заглянуть в настройки, а то мало ли что...', reply_markup=keyboard_main)
    upd_b()


@bot.message_handler(content_types=["text"])  # ответ на любой текст
def any_msg(message):
    if message.text.lower() == 'статы':
        ind = get_id(message.chat.id)
        bot.send_message(message.chat.id, "твои статы:\nправильных ответов: " + str(ids[ind].correct)
                         + "\nнеправильных ответов: " + str(ids[ind].wrong)
                         + "\nразблокировано слов: " + str(sum(ids[ind].used)) + " / " + str(len(words)))
        return
    elif message.text.lower() == 'топ':
        ids.sort(key=comparator, reverse=True)
        s = "текущий топ по количеству правильных ответов:\n"
        place = 1
        for i in range(len(ids)):
            if ids[i].top == 0:
                continue
            s += str(place) + ") " + str(ids[i].correct) + " "
            s += "- "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += '\n'
            place += 1
        bot.send_message(message.chat.id, s)
        return
    elif message.text.lower() == 'настройки':
        bot.send_message(message.chat.id, "да, настроек пока маловато... но это же лучше, чем ничего?", reply_markup=keyboard_settings)
    elif message.text.lower() == 'настройки отображения в топе':
        bot.send_message(message.chat.id, "отображать ли тебя в топе?", reply_markup=callback_buttons_top)
    elif message.text.lower() == 'выйти из настроек':
        bot.send_message(message.chat.id, "скорее всего, выйти из настроек можно без сообщения, но я не смог нагуглить то, как это сделать, поэтому могу просто сказать, что на " + str(randint(0, 100)) + "% ты лох))))))", reply_markup=keyboard_main)
    elif message.text.lower() == 'слово!':
        ind_ids = get_id(message.chat.id)
        if sum(ids[ind_ids].used) == len(words):
            ids[ind_ids].used.clear()

        to_send = 'поставь ударение в слове '
        while 1:
            word_ind = randint(0, len(words) - 1)
            if ids[ind_ids].used[word_ind] == 0:
                s = words[word_ind]
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
    else:
        print(message.from_user.first_name, message.from_user.last_name, "сказал", message.text)
        upd_b()
        bot.send_message(message.chat.id, "я, скорее всего, еще туповат, чтобы понять, что тут написано...")


@bot.callback_query_handler(func=lambda call: True)  # реакция на ответ на задачу
def callback_inline(call):
    if len(call.data) >= 4 and call.data[:4] == "good":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="правильно! ответ: " + link[call.data[4:].lower()])
        ind = get_id(call.message.chat.id)
        ids[ind].correct += 1
        ids[ind].last_answer = get_time()
        ids[ind].skipped = 0
        ids[ind].used[words.index(link[call.data[4:].lower()].lower())] = 1
        if (sum(ids[ind].used) == len(words)):
            bot.send_message(chat_id=call.message.chat.id, text="поздравляем! все слова были разблокированы!")
        upd_b()
    elif len(call.data) >= 3 and call.data[:3] == "bad":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="неправильно... ответ был: " + link[call.data[3:].lower()])
        ind = get_id(call.message.chat.id)
        ids[ind].wrong += 1
        ids[ind].last_answer = get_time()
        ids[ind].skipped = 0
        upd_b()
    elif len(call.data) >= 7 and call.data[:7] == "top_yes":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="окей! надеюсь, ты сможешь покорить вершину!")
        ind = get_id(call.message.chat.id)
        ids[ind].top = 1
    elif len(call.data) >= 6 and call.data[:6] == "top_no":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="хорошо, скрываю тебя...")
        ind = get_id(call.message.chat.id)
        ids[ind].top = 0


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
