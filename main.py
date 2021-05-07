import operator
import telebot
from telebot import types
from random import randint
from time import sleep
from functools import wraps
from datetime import datetime


class User:
    def __init__(self, id, correct, wrong, last_answer, first_name, last_name, skipped, top, rating, streak, max_streak, used, achievements):
        self.id = id
        self.correct = correct
        self.wrong = wrong
        self.last_answer = last_answer
        self.first_name = first_name
        self.last_name = last_name
        self.skipped = skipped
        self.top = top
        self.rating = rating
        self.used = used
        self.achievements = achievements
        self.streak = streak
        self.max_streak = max_streak


# used[i][0] = сколько раз задавался вопрос со словом i за сессию, used[i][1] = 0/1 был ли правильный ответ на вопрос со словом i


words = []
ids = []
link = {}
global timer
all_achievements = ['разблокировать все слова',
                    '100 правильных слов',
                    '500 правильных слов',
                    '1000 правильных слов',
                    'топ\-1 по рейтингу',
                    'топ\-1 по стрику',
                    'топ\-1 по % правильных ответов',
                    'стрик 10',
                    'стрик 50',
                    'стрик 100',
                    'стрик 250',
                    'a big secret']
ranks = ["победитель \"Русского медвежонка\"",
         "победитель ВСоШ по русскому языку", "призер ВСоШ по русскому языку", "участник ВСоШ по русскому языку",
         "победитель региона по русскому языку", "призер региона по русскому языку", "участник региона по русскому языку",
         "победитель муниципа по русскому языку", "призер муниципа по русскому языку", "участник муниципа по русскому языку",
         "победитель школьного этапа по русскому языку", "призер школьного этапа по русскому языку", "участник школьного этапа по русскому языку"]


#клавиатуры_start

keyboard_main = types.ReplyKeyboardMarkup(True, False)
keyboard_main.row('слово!', 'статы', 'топ')
keyboard_main.add('достижения', 'помощь', 'настройки')
keyboard_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_settings.row('настройки отображения в топе', 'главное меню')
keyboard_choose_top = types.ReplyKeyboardMarkup(True, False)
keyboard_choose_top.row('топ по рейтингу', 'топ по стрику', 'топ по % правильных', 'главное меню')

# топ

keyboard_top_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_top_settings.row('вкл/выкл отображение в топе', 'обновить мое имя в топе', 'вернуться к меню настроек')

# отображение в топе
callback_buttons_top = types.InlineKeyboardMarkup()
callback_button_top1 = types.InlineKeyboardButton(text="да", callback_data="top_yes")
callback_button_top2 = types.InlineKeyboardButton(text="нет", callback_data="top_no")
callback_buttons_top.add(callback_button_top1)
callback_buttons_top.add(callback_button_top2)

#клавиатуры_end


# algo
def algo():
    n = open("udars.txt", "r", encoding="utf-8")
    t = n.readlines()
    ok = 1
    for i in t:
        if ok == 0:
            ok = 1
            continue
        if i == "\n":
            continue
        temp = i.split("\n")
        if words.count(temp[0]) == 0:
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
    text_main = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_main_info.txt", "r")
    text_used = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_used_info.txt", "r")
    text_achievements = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_achievements_info.txt", "r")
    users = 0
    for _ in text_main:
        users += 1
    text_main.close()
    used_local = [[[0] * 2 for _ in range(len(words))] for i in range(users)]
    achievements_local = [[0] * len(all_achievements) for _ in range(users)]
    ind = 0
    for line in text_used:
        a = line.split()
        for i in range(len(words)):
            used_local[ind][i][0] = int(a[2 * i + 1])
            used_local[ind][i][1] = int(a[2 * i + 1 + 1])
        ind += 1
    ind = 0
    for line in text_achievements:
        a = line.split()
        for i in range(len(all_achievements)):
            achievements_local[ind][i] = int(a[i + 1])
        ind += 1
    ind = 0
    text_main = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_main_info.txt", "r")
    for line in text_main:
        a = line.split()
        ids.append(User(int(a[0]),
                        int(a[1]),
                        int(a[2]),
                        int(a[3]),
                        a[4],
                        a[5],
                        int(a[6]),
                        int(a[7]),
                        int(a[8]),
                        int(a[9]),
                        int(a[10]),
                        used_local[ind], achievements_local[ind]))
        ind += 1


algo()
print('algo ok, loaded', len(words), 'words')
start_prog()
print('start_prog ok, loaded', len(ids), 'users')
# algo
bot = telebot.TeleBot('1639467970:AAEXXyaLvwq1LIe9rOMjo0AzyhMlVKl-3Xc')


def upd_b():
    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_main_info.txt", "r")
    file2 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_main_info_backup.txt", "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_main_info.txt", "w")
    file1.truncate(0)
    for i in range(len(ids)):
        file1.write(str(ids[i].id) + ' '
                    + str(ids[i].correct) + ' '
                    + str(ids[i].wrong) + ' '
                    + str(ids[i].last_answer) + ' '
                    + str(ids[i].first_name) + ' '
                    + str(ids[i].last_name) + ' '
                    + str(ids[i].skipped) + ' '
                    + str(ids[i].top) + ' '
                    + str(ids[i].rating) + ' '
                    + str(ids[i].streak) + ' '
                    + str(ids[i].max_streak) + '\n')
    file1.close()

    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_used_info.txt", "r")
    file2 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_used_info_backup.txt", "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_used_info.txt", "w")
    file1.truncate(0)
    for i in range(len(ids)):
        used_write = ""
        for j in range(len(ids[i].used)):
            used_write += str(ids[i].used[j][0]) + ' ' + str(ids[i].used[j][1]) + ' '
        file1.write(str(ids[i].id) + ' ' + used_write + '\n')
    file1.close()

    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_achievements_info.txt", "r")
    file2 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_achievements_info_backup.txt", "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(r"C:\Users\tydo_\a\rus_ege_bot\dbs\db_achievements_info.txt", "w")
    file1.truncate(0)
    for i in range(len(ids)):
        ach_write = ""
        for j in range(len(ids[i].achievements)):
            ach_write += str(ids[i].achievements[j]) + ' '
        file1.write(str(ids[i].id) + ' ' + ach_write + '\n')
    file1.close()
    print('dbs updated')


def get_time():
    date = datetime.now()
    # print(date.month, date.day, date.hour, date.minute, date.second)
    ret = date.hour + date.day * 24 + date.month * 31
    return ret


def comparator_rating(a):
    if a.top == 0:
        return -1e10
    return a.rating


def comparator_streak(a):
    if a.top == 0:
        return -1e10
    return a.max_streak


def comparator_percent(a):
    if a.top == 0 or a.correct + a.wrong < 100:
        return -1e10
    return round(a.correct / (a.correct + a.wrong) * 100.0, 2)


def get_id(message_id):
    ind = -1
    for i in range(len(ids)):
        if ids[i].id == message_id:
            ind = i
            break

    return ind


def get_sum(ind):
    sum = 0
    for i in range(len(words)):
        sum += ids[ind].used[i][1]
    return sum


@bot.message_handler(commands=['start'])  # ответ на команду /start
def start(message):
    ind = get_id(message.chat.id)
    if ind != -1:
        print(ids[ind].first_name, ids[ind].last_name, 'said /start')
        bot.reply_to(message, f'мы уже здоровались!', reply_markup=keyboard_main)
        return
    print('new user', message.chat.first_name, message.chat.last_name , 'said /start')
    new_used = [[0] * 2 for i in range(len(words))]
    new_ach = [0] * len(all_achievements)
    ids.append(User(message.chat.id, 0, 0, get_time(), message.chat.first_name, message.chat.last_name, 0, 1, 0, 0, 0, new_used, new_ach))
    print('registered', message.chat.first_name, message.chat.last_name, 'with ind', get_id(message.chat.id))
    bot.reply_to(message, f'привет! готов закидать тебя словами! советую заглянуть в настройки, а то мало ли что...', reply_markup=keyboard_main)
    upd_b()

@bot.message_handler(content_types=["text"])  # ответ на любой текст
def any_msg(message):
    print(message.chat.first_name, message.chat.last_name, 'said', message.text)
    ind = get_id(message.chat.id)
    if message.text.lower() == 'статы':
        ids.sort(key=comparator_rating, reverse=True)
        ind = get_id(message.chat.id)

        sum = get_sum(ind)
        if ids[ind].achievements[0] == 1:
            sum = len(words)
        top = str(ind + 1)
        zvanie = ranks[min(len(ranks) - 1, ind)]
        if ids[ind].top == 0:
            top = "ты не отображаешься в топе =("
            zvanie = "нет в топе - нет звания("
        if ids[ind].streak >= 50:
            streak = '+' + str(ids[ind].streak) + '🔥'
        elif ids[ind].streak > 0:
            streak = '+' + str(ids[ind].streak)
        elif ids[ind].streak < 0:
            streak = str(ids[ind].streak)
        else:
            streak = '0'
        if ids[ind].max_streak > 0:
            max_str = "+" + str(ids[ind].max_streak)
        else:
            max_str = str(ids[ind].max_streak)
        bot.send_message(message.chat.id,
                         "личная статистика.\nрейтинг: " + str(ids[ind].rating)
                         + "\nместо в топе: " + top
                         + "\nзвание: " + zvanie
                         + "\nправильных ответов: " + str(ids[ind].correct)
                         + "\nнеправильных ответов: " + str(ids[ind].wrong)
                         + "\nтекущий стрик: " + streak
                         + "\nмаксимальный стрик: " + max_str
                         + "\nразблокировано слов: " + str(sum) + " / " + str(len(words)), reply_markup=keyboard_main)
        print('gave', message.chat.first_name, message.chat.last_name, 'stats')
    elif message.text.lower() == 'топ':
        bot.send_message(message.chat.id, 'выбери, какой топ хочешь посмотреть', reply_markup=keyboard_choose_top)
    elif message.text.lower() == 'топ по рейтингу':
        ids.sort(key=comparator_rating, reverse=True)
        s = "текущий топ по рейтингу:\n"
        place = 0
        for i in range(len(ids)):
            zvanie = ranks[min(len(ranks) - 1, place)]
            if ids[i].top == 0:
                continue
            s += str(place + 1) + ") "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += "| " + str(ids[i].rating) + " | " + zvanie + "\n"
            place += 1
        bot.send_message(message.chat.id, s, reply_markup=keyboard_choose_top)
        print('gave', message.chat.first_name, message.chat.last_name, 'top_rate')
    elif message.text.lower() == 'топ по стрику':
        ids.sort(key=comparator_streak, reverse=True)
        s = "текущий топ по стрику:\n"
        place = 0
        for i in range(len(ids)):
            if ids[i].top == 0:
                continue
            s += str(place + 1) + ") "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            if ids[i].max_streak > 0:
                max_str = "+ " + str(ids[i].max_streak)
            else:
                max_str = str(ids[i].max_streak)
            s += "| " + max_str + "\n"
            place += 1
        bot.send_message(message.chat.id, s, reply_markup=keyboard_choose_top)
        print('gave', message.chat.first_name, message.chat.last_name, 'top_streak')
    elif message.text.lower() == 'топ по % правильных':
        ids.sort(key=comparator_percent, reverse=True)
        s = "текущий топ по % правильных ответов (пользователи с количеством ответов не меньше 100):\n"
        place = 0
        for i in range(len(ids)):
            if ids[i].top == 0 or ids[i].correct + ids[i].wrong < 100:
                continue
            s += str(place + 1) + ") "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += str(round(ids[i].correct / (ids[i].correct + ids[i].wrong) * 100.0, 2)) + "% (" + str(ids[i].correct) + " правильных из " + str(ids[i].wrong + ids[i].correct) + ")\n"
            place += 1
        bot.send_message(message.chat.id, s, reply_markup=keyboard_choose_top)
        print('gave', message.chat.first_name, message.chat.last_name, 'top_percent')
    elif message.text.lower() == 'настройки' or message.text.lower() == 'вернуться к меню настроек':
        bot.send_message(message.chat.id, "да, настроек пока маловато... но это же лучше, чем ничего?", reply_markup=keyboard_settings)
        print('gave', message.chat.first_name, message.chat.last_name, 'settings')
    elif message.text.lower() == 'настройки отображения в топе':
        bot.send_message(message.chat.id, "телепортирую в настройки отображения в топе...",
                         reply_markup=keyboard_top_settings)
        print('gave', message.chat.first_name, message.chat.last_name, 'top settings')
    elif message.text.lower() == 'вкл/выкл отображение в топе':
        bot.send_message(message.chat.id, "отображать ли тебя в топе?", reply_markup=callback_buttons_top)
        print('gave', message.chat.first_name, message.chat.last_name, 'settings in top')
    elif message.text.lower() == 'обновить мое имя в топе':
        ind = get_id(message.chat.id)
        print(ids[ind].first_name, ids[ind].last_name, 'changed name to', end=" ")
        bot.send_message(message.chat.id, "изменил твое имя в соответствии с твоим телеграм-аккаунтом!")
        ids[ind].first_name = message.chat.first_name
        ids[ind].last_name = message.chat.last_name
        print(message.chat.first_name, message.chat.last_name)
        upd_b()
    elif message.text.lower() == 'главное меню':
        bot.send_message(message.chat.id, "скорее всего, выйти в главное меню можно без сообщения, но я не смог нагуглить то, как это сделать, поэтому могу просто сказать, что в данный момент на " + str(randint(0, 100)) + "% ты лох))))))", reply_markup=keyboard_main)
        print('gave', message.chat.first_name, message.chat.last_name, 'exit from settings')
    elif message.text.lower() == 'достижения':
        ind = get_id(message.chat.id)
        text = "достижения🏆\n"
        for i in range(len(all_achievements)):
            if ids[ind].achievements[i] == 1:
                text += str(i + 1) + "\) " + all_achievements[i]
            else:
                text += str(i + 1) + "\) ~" + all_achievements[i] + "~"
            text += '\n'
        bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')
        print('gave', message.chat.first_name, message.chat.last_name, 'achievements')
    elif message.text.lower() == 'слово!':
        ind_ids = get_id(message.chat.id)
        sum = get_sum(ind_ids)
        if sum == len(words):
            ids[ind_ids].used.clear()
            ids[ind_ids].used = [[0] * 2 for i in range(len(words))]

        to_send = 'поставь ударение в слове '
        while 1:
            word_ind = randint(0, len(words) - 1)
            if ids[ind_ids].used[word_ind][1] == 0:
                s = words[word_ind]
                break
        ids[ind_ids].used[word_ind][0] += 1
        to_send += '*' + s + '*'
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
        bot.send_message(message.chat.id, to_send, reply_markup=keyboard, parse_mode='MarkdownV2')
        print('gave', message.chat.first_name, message.chat.last_name, 'word', words[word_ind])
        upd_b()
    elif message.text.lower() == 'помощь':
        bot.send_message(message.chat.id, "по всем вопросам писать @Rustam_Fakhretdinov", reply_markup=keyboard_main)
        print('help', message.chat.first_name, message.chat.last_name)
    elif message.text.lower() == '444' and ids[ind].achievements[11] == 0:
        bot.send_message(chat_id=message.chat.id, text="получено достижение🏆\!\na big secret\!\n_so, why 444\?\.\._", parse_mode='MarkdownV2')
        ids[ind].achievements[11] = 1
        print(message.chat.first_name, message.chat.last_name, 'got achievement 11')
        upd_b()
    else:
        print(message.from_user.first_name, message.from_user.last_name, "said", message.text)
        upd_b()
        bot.send_message(message.chat.id, "я, скорее всего, еще туповат, чтобы понять, что тут написано...", reply_markup=keyboard_main)


@bot.callback_query_handler(func=lambda call: True)  # реакция на callback кнопки
def callback_inline(call):
    if len(call.data) >= 4 and call.data[:4] == "good":
        ind = get_id(call.message.chat.id)
        if ids[ind].used[words.index(link[call.data[4:].lower()].lower())][0] >= 1:
            r = 1
            ed_r = " единицу рейтинга"
        else:
            r = 2
            ed_r = " единицы рейтинга"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="правильно✅\nответ: " + link[call.data[4:].lower()] + "\nты получил " + str(r) + ed_r)
        ids[ind].correct += 1
        ids[ind].last_answer = get_time()
        ids[ind].skipped = 0
        ids[ind].used[words.index(link[call.data[4:].lower()].lower())][1] = 1
        ids[ind].rating += r
        if ids[ind].streak < 0:
            ids[ind].streak = 1
        else:
            ids[ind].streak += 1
        ids[ind].max_streak = max(ids[ind].max_streak, ids[ind].streak)
        print(call.message.chat.first_name, call.message.chat.last_name, 'answered', link[call.data[4:].lower()].lower(), 'correct, +', r, 'rating')

        # achievements
        if get_sum(ind) == len(words) and ids[ind].achievements[0] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\nвсе слова были разблокированы!")
            ids[ind].achievements[0] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 0')
        if ids[ind].correct >= 100 and ids[ind].achievements[1] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n100 правильных слов!")
            ids[ind].achievements[1] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 1')
        if ids[ind].correct >= 500 and ids[ind].achievements[2] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n500 правильных слов!\nэто круто! продолжай в том же духе! =)")
            ids[ind].achievements[2] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 2')
        if ids[ind].correct >= 1000 and ids[ind].achievements[3] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n1000 правильных слов!\nэто очень много...")
            ids[ind].achievements[3] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 3')

        ids.sort(key=comparator_rating, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[4] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по рейтингу!\nты на вершине! поздравляю!")
            ids[ind].achievements[4] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 4')
        ids.sort(key=comparator_streak, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[5] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по стрику!\nты на вершине! поздравляю!")
            ids[ind].achievements[5] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 5')
        ids.sort(key=comparator_streak, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[6] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по % правильных ответов!\nты на вершине! поздравляю!")
            ids[ind].achievements[6] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 6')

        if ids[ind].max_streak >= 10 and ids[ind].achievements[7] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 10!\nсильно. но можно сильнее.")
            ids[ind].achievements[7] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 7')
        if ids[ind].max_streak >= 50 and ids[ind].achievements[8] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 50!\nда ты в ударе🔥🔥🔥")
            ids[ind].achievements[8] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 8')
        if ids[ind].max_streak >= 100 and ids[ind].achievements[9] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 100!\nтакое реально вообще?! жесть...")
            ids[ind].achievements[9] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 9')
        if ids[ind].max_streak >= 250 and ids[ind].achievements[10] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 250!\nпохоже, что ты всё выучил... поздравляю!")
            ids[ind].achievements[10] = 1
            print(call.message.chat.first_name, call.message.chat.last_name, 'got achievement 10')
        upd_b()
    elif len(call.data) >= 3 and call.data[:3] == "bad":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="неправильно❌\nответ был: " + link[call.data[3:].lower()] + "\nты потерял 1 единицу рейтинга")
        print(call.message.chat.first_name, call.message.chat.last_name, 'answered',
              link[call.data[3:].lower()].lower(), 'wrong, -1 rating')
        ind = get_id(call.message.chat.id)
        ids[ind].wrong += 1
        ids[ind].last_answer = get_time()
        ids[ind].skipped = 0
        ids[ind].rating -= 1
        ids[ind].rating = max(ids[ind].rating, 0)
        if ids[ind].streak > 0:
            ids[ind].streak = -1
        else:
            ids[ind].streak -= 1
        upd_b()
    elif len(call.data) >= 7 and call.data[:7] == "top_yes":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="окей! надеюсь, ты сможешь покорить вершину!")
        ind = get_id(call.message.chat.id)
        print(call.message.chat.first_name, call.message.chat.last_name, 'now in top')
        ids[ind].top = 1
        upd_b()
    elif len(call.data) >= 6 and call.data[:6] == "top_no":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="хорошо, скрываю тебя...")
        ind = get_id(call.message.chat.id)
        print(call.message.chat.first_name, call.message.chat.last_name, 'now not in top')
        ids[ind].top = 0
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
            if nowtime - int(ids[i].last_answer) >= 5 and ids[i].skipped < 3:
                ids[i].skipped += 1
                print('notification for', ids[i].first_name, ids[i].last_name)
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! для тебя есть новое задание! если хочешь получить, нажми на кнопочку)")
            elif ids[i].skipped >= 3 and ids[i].skipped < 4 and nowtime - int(ids[i].last_answer) >= 10:
                ids[i].skipped += 1
                print('notification for', ids[i].first_name, ids[i].last_name)
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! давно тебя не было в уличных гонках! если хочешь получить вопросик, нажми на кнопочку)")
            elif ids[i].skipped >= 4 and ids[i].skipped < 5 and nowtime - int(ids[i].last_answer) >= 10:
                ids[i].skipped += 1
                print('last notification for', ids[i].first_name, ids[i].last_name)
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! последний раз предлагаю тебе вспомнить про ударения на егэ!")


test()
bot.polling(none_stop=True, interval=0)
