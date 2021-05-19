import os
import telebot
import logging
import schedule
import time
import sys
from telebot import types
from random import randint
from time import sleep
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(encoding='utf8')


global timer
words = []
ids = []
link = {}
BOT_TOKEN = os.getenv('BOT_TOKEN')
MAIN_INFO = os.getenv('MAIN_INFO')
MAIN_INFO_BACKUP = os.getenv('MAIN_INFO_BACKUP')
USED_INFO = os.getenv('USED_INFO')
USED_INFO_BACKUP = os.getenv('USED_INFO_BACKUP')
ACHIEVEMENTS_INFO = os.getenv('ACHIEVEMENTS_INFO')
ACHIEVEMENTS_INFO_BACKUP = os.getenv('ACHIEVEMENTS_INFO_BACKUP')
LOGS_PATH = os.getenv('LOGS_PATH')
BANNED_USERS = os.getenv('BANNED_USERS')
BANNED_USERS_BACKUP = os.getenv('BANNED_USERS_BACKUP')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
bot = telebot.TeleBot(BOT_TOKEN)

# logs

nowtimestr = str(datetime.now())
nowtimestr = nowtimestr.replace(' ', '-')
nowtimestr = nowtimestr.replace('.', '-')
nowtimestr = nowtimestr.replace(':', '-')
path = LOGS_PATH + "bot-" + nowtimestr + ".log"
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", filename=path, filemode="w", encoding='utf-8')

#


def get_time():
    date = datetime.now()
    # print(date.month, date.day, date.hour, date.minute, date.second)
    ret = str(date.day) + '-' + str(date.month) + '-' + str(date.year) + ':' + str(date.hour) + '-' + str(date.minute) + '-' + str(date.second)
    return ret


def get_time_for_notif():
    date = datetime.now()
    # print(date.month, date.day, date.hour, date.minute, date.second)
    ret = date.hour + date.day * 24 + date.month * 31
    return ret


class User:
    def __init__(self, id, correct, wrong, last_answer, first_name, last_name, skipped, top, rating, streak, max_streak, notify_game, notify_admin, banned, used, achievements):
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
        self.banned = banned
        self.notify_game = notify_game
        self.notify_admin = notify_admin


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
         "победитель ВСоШ по русскому языку",
         "призер ВСоШ по русскому языку",
         "участник ВСоШ по русскому языку",
         "победитель региона по русскому языку",
         "призер региона по русскому языку",
         "участник региона по русскому языку",
         "победитель муниципа по русскому языку",
         "призер муниципа по русскому языку",
         "участник муниципа по русскому языку",
         "победитель школьного этапа по русскому языку",
         "призер школьного этапа по русскому языку",
         "участник школьного этапа по русскому языку"]

#клавиатуры_start

keyboard_main = types.ReplyKeyboardMarkup(True, False)
keyboard_main.row('слово!', 'статы', 'топ')
keyboard_main.add('достижения', 'помощь', 'настройки')
keyboard_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_settings.row('настройки отображения в топе', 'сбросить прогресс', 'настройки уведомлений')
keyboard_settings.row('главное меню')
keyboard_choose_top = types.ReplyKeyboardMarkup(True, False)
keyboard_choose_top.row('топ по рейтингу', 'топ по стрику')
keyboard_choose_top.add('топ по % правильных', 'главное меню')

# топ

keyboard_top_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_top_settings.row('вкл/выкл отображение в топе', 'обновить мое имя в топе', 'вернуться к меню настроек')

# настройки уведомлений

keyboard_notification_settings = types.ReplyKeyboardMarkup(True, False)
keyboard_notification_settings.row('вкл. напоминания', 'выкл. напоминания')
keyboard_notification_settings.row('вкл. оповещения', 'выкл. оповещения')
keyboard_notification_settings.row('вкл. все уведомления', 'выкл. все уведомления')
keyboard_notification_settings.row('вернуться к меню настроек')

# отображение в топе
callback_buttons_top = types.InlineKeyboardMarkup()
callback_button_top1 = types.InlineKeyboardButton(text="да", callback_data="top_yes")
callback_button_top2 = types.InlineKeyboardButton(text="нет", callback_data="top_no")
callback_buttons_top.add(callback_button_top1)
callback_buttons_top.add(callback_button_top2)

callback_buttons_loseprogress = types.InlineKeyboardMarkup()
callback_buttons_loseprogress1 = types.InlineKeyboardButton(text="да", callback_data="loseprog_yes")
callback_buttons_loseprogress2 = types.InlineKeyboardButton(text="нет", callback_data="loseprog_no")
callback_buttons_loseprogress.add(callback_buttons_loseprogress1, callback_buttons_loseprogress2)

#клавиатуры_end


def words_fill():
    n = open("udareniya.txt", "r", encoding="utf-8")
    t = n.readlines()
    for i in t:
        temp = i.split("\n")
        if words.count(temp[0]) == 0:
            words.append(temp[0])

    for i in range(len(words)):
        s = words[i]
        for j in range(len(s)):
            if s[j] == s[j].upper():
                link[s.lower()] = s
                break
    for i in range(len(words)):
        words[i] = words[i].lower()
    n.close()

    words_debug = "words:\n"
    for i in range(len(words)):
        words_debug += str(i) + ')' + words[i] + "\n"
    print(words_debug)
    logging.debug(words_debug)


def start_prog():
    text_main = open(MAIN_INFO, "r", encoding='utf8')
    text_used = open(USED_INFO, "r")
    text_achievements = open(ACHIEVEMENTS_INFO, "r")
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
    text_used.close()
    text_achievements.close()

    text_main = open(MAIN_INFO, "r", encoding='utf8')
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
                        int(a[11]),
                        int(a[12]),
                        int(a[13]),
                        used_local[ind], achievements_local[ind]))
        ind += 1
    text_main.close()

    ids_debug = "users:\n"
    for i in range(len(ids)):
        ids_debug += str(i) + ") " + str(ids[i].id) + ' ' + ids[i].first_name + ' ' + ids[i].last_name + "\n"
    logging.debug(ids_debug)


def setup():
    words_fill()
    print(get_time() + ':: words loaded, count= ' + str(len(words)))
    logging.info('words loaded, count= ' + str(len(words)))
    start_prog()
    print(get_time() + ':: ' + 'users loaded, count= ' + str(len(ids)))
    logging.info('users loaded, count= ' + str(len(ids)))


def upd_b():
    file1 = open(MAIN_INFO, "r", encoding='utf8')
    file2 = open(MAIN_INFO_BACKUP, "w", encoding='utf8')
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(MAIN_INFO, "w", encoding='utf8')
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
                    + str(ids[i].max_streak) + ' '
                    + str(ids[i].notify_game) + ' '
                    + str(ids[i].notify_admin) + ' '
                    + str(ids[i].banned) + '\n')
    file1.close()

    logging.debug('main info database updated')

    file1 = open(USED_INFO, "r")
    file2 = open(USED_INFO_BACKUP, "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(USED_INFO, "w")
    file1.truncate(0)
    for i in range(len(ids)):
        used_write = ""
        for j in range(len(ids[i].used)):
            used_write += str(ids[i].used[j][0]) + ' ' + str(ids[i].used[j][1]) + ' '
        file1.write(str(ids[i].id) + ' ' + used_write + '\n')
    file1.close()

    logging.debug('used info database updated')

    file1 = open(ACHIEVEMENTS_INFO, "r")
    file2 = open(ACHIEVEMENTS_INFO_BACKUP, "w")
    file2.truncate(0)
    for line in file1:
        file2.write(line)
    file1.close()
    file2.close()
    file1 = open(ACHIEVEMENTS_INFO, "w")
    file1.truncate(0)
    for i in range(len(ids)):
        ach_write = ""
        for j in range(len(ids[i].achievements)):
            ach_write += str(ids[i].achievements[j]) + ' '
        file1.write(str(ids[i].id) + ' ' + ach_write + '\n')
    file1.close()
    logging.debug('achievement info database updated')
    print(get_time() + ':: ' + 'all databases updated')
    logging.info('all databases updated')


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


def get_names_msg(message):
    name = message.chat.first_name
    fam = message.chat.last_name
    if str(message.chat.first_name) != "None":
        name = name.replace(' ', '_')
    else:
        name = "None"
    if str(message.chat.last_name) != "None":
        fam = fam.replace(' ', '_')
    else:
        fam = "None"
    return str(name) + ' ' + str(fam)


def get_names_ind(ind):
    return str(ids[ind].first_name) + ' ' + str(ids[ind].last_name)


def upd_chatid(message):
    for i in range(len(ids)):
        if message.chat.first_name == ids[i].first_name and message.chat.id != ids[i].id:
            ids[i].id = message.chat.id
            print(get_names_msg(message), 'UPDATED CHAT ID')
            upd_b()
            break


def replace_mark(s):
    s = s.replace('_', '\_')
    s = s.replace(')', '\)')
    s = s.replace('(', '\(')
    s = s.replace('-', '\-')
    s = s.replace('+', '\+')
    s = s.replace('%', '\%')
    s = s.replace('.', '\.')
    s = s.replace('[', '\[')
    s = s.replace(']', '\]')
    s = s.replace('-', '\-')
    s = s.replace('`', '\`')
    s = s.replace('{', '\{')
    s = s.replace('}', '\}')
    s = s.replace('https:', '\[banned\]')
    s = s.replace('.com', '\[banned\]')
    s = s.replace('.ru', '\[banned\]')
    s = s.replace('.net', '\[banned\]')
    return s


def lose_progress(id):
    for i in range(len(ids)):
        if ids[i].id == id:
            new_used = [[0] * 2 for i in range(len(words))]
            new_ach = [0] * len(all_achievements)
            ids[i].correct = 0
            ids[i].wrong = 0
            ids[i].skipped = 0
            ids[i].top = 1
            ids[i].rating = 0
            ids[i].used = new_used
            ids[i].achievements = new_ach
            ids[i].streak = 0
            ids[i].max_streak = 0
            break


def is_banned(message):
    if ids[get_id(message.chat.id)].banned == 1:
        try:
            bot.send_message(message.chat.id, 'ты забанен :( \nпо вопросам разбана - @Rustam_Fakhretdinov')
            logging.info(get_names_msg(message) + ' is banned, got message from bot about ban')
            print(get_time() + ':: ' + get_names_msg(message) + ' is banned, got message from bot about ban')
        except telebot.apihelper.ApiException:
            logging.error(get_names_msg(message) + ' is banned, cant send message to him ' + message.text)
            print(get_time() + ':: ' + get_names_msg(message) + ' is banned, cant send message to him')
        return 1
    return 0


@bot.message_handler(commands=['start'])  # ответ на команду /start
def start(message):
    logging.info(get_names_msg(message) + ' pressed /start')
    print(get_time() + ':: ' + get_names_msg(message) + ' pressed /start')
    ind = get_id(message.chat.id)
    if ind != -1:
        bot.reply_to(message, f'мы уже здоровались!', reply_markup=keyboard_main)
        return
    new_used = [[0] * 2 for _ in range(len(words))]
    new_ach = [0] * len(all_achievements)

    name = message.chat.first_name
    fam = message.chat.last_name
    if str(message.chat.first_name) != "None":
        name = name.replace(' ', '_')
    else:
        name = "None"
    if str(message.chat.last_name) != "None":
        fam = fam.replace(' ', '_')
    else:
        fam = "None"

    fam = fam.replace(' ', '_')
    ids.append(User(message.chat.id, 0, 0, get_time_for_notif(), name, fam, 0, 1, 0, 1, 0, 1, 1, 0, new_used, new_ach))
    bot.reply_to(message, f'привет! готов закидать тебя словами! советую заглянуть в настройки, а то мало ли что...', reply_markup=keyboard_main)

    print(get_time() + ':: ' + 'registered @' + str(message.from_user.username) + ' ' + get_names_msg(message) + ' with ind ' + str(get_id(message.chat.id)))
    logging.info('registered @' + str(message.from_user.username) + ' ' + get_names_msg(message) + ' with ind ' + str(get_id(message.chat.id)))
    upd_b()


@bot.message_handler(commands=['ban'])  # ответ на команду /ban
def ban(message):
    if message.chat.id != ADMIN_ID:
        return
    text = message.text.split()
    chat_id = int(text[1])
    ind = get_id(chat_id)
    ids[ind].banned = 1
    print(get_time() + ':: ' + get_names_ind(ind) + ' has been banned')
    logging.info(get_names_ind(ind) + ' has been banned')
    upd_b()


@bot.message_handler(commands=['unban'])  # ответ на команду /ban
def ban(message):
    if message.chat.id != ADMIN_ID:
        return
    text = message.text.split()
    chat_id = int(text[1])
    ind = get_id(chat_id)
    ids[ind].banned = 0
    print(get_time() + ':: ' + get_names_ind(ind) + ' has been unbanned')
    logging.info(get_names_ind(ind) + ' has been unbanned')
    upd_b()


@bot.message_handler(commands=['post'])  # ответ на команду /post
def post(message):
    if message.chat.id != ADMIN_ID:
        return
    text = message.text
    text = text[6:]
    for i in range(len(ids)):
        if ids[i].notify_admin == 0 or ids[i].banned == 1:
            continue
        try:
            bot.send_message(ids[i].id, text, reply_markup=keyboard_main, disable_notification=1)
            print(get_time() + ':: ' + 'posted to: ' + get_names_ind(i) + ' text:' + text)
            logging.info('posted: ' + 'posted to: ' + get_names_ind(i) + ' text:' + text)
        except telebot.apihelper.ApiException:
            logging.error('cant send message to ' + get_names_ind(i))
            print(get_time() + ':: ' + 'cant send message to ' + get_names_ind(i))

    print(get_time() + ':: ' + 'posted')
    logging.info('posted')
    upd_b()


@bot.message_handler(commands=['post_prev'])  # ответ на команду /post_prev
def post_prev(message):
    if message.chat.id != ADMIN_ID:
        return
    text = message.text
    text = text[11:]
    bot.send_message(ADMIN_ID, "text preview is:\n" + text, reply_markup=keyboard_main, disable_notification=1)


@bot.message_handler(content_types=["text"])  # ответ на любой текст
def any_msg(message):
    upd_chatid(message)
    logging.info(get_names_msg(message) + ' texted ' + message.text)
    print(get_time() + ':: ' + get_names_msg(message) + ' texted ' + message.text)

    if is_banned(message) == 1:
        return

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
            top = "ты не отображаешься в топе \=\("
            zvanie = "нет в топе \- нет звания\("
        if ids[ind].banned == 1:
            top = "ты в бане, тебя нет в топе \=\("
            zvanie = "с позором забаненный"
        if ids[ind].streak >= 50:
            streak = '\+' + str(ids[ind].streak) + '🔥'
        elif ids[ind].streak > 0:
            streak = '\+' + str(ids[ind].streak)
        elif ids[ind].streak < 0:
            streak = str(ids[ind].streak)
        else:
            streak = '0'
        if ids[ind].max_streak > 0:
            max_str = "\+" + str(ids[ind].max_streak)
        else:
            max_str = str(ids[ind].max_streak)
        streak = streak.replace('-', '\-')
        max_str = max_str.replace('-', '\-')
        bot.send_message(message.chat.id,
                         "*личная статистика\.*\nрейтинг: " + str(ids[ind].rating)
                         + "\nместо в топе: " + top
                         + "\nзвание: " + zvanie
                         + "\nправильных ответов: " + str(ids[ind].correct)
                         + "\nнеправильных ответов: " + str(ids[ind].wrong)
                         + "\nтекущий стрик: " + streak
                         + "\nмаксимальный стрик: " + max_str
                         + "\nразблокировано слов: " + str(sum) + " / " + str(len(words)), reply_markup=keyboard_main, parse_mode='MarkdownV2')

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' stats')
        logging.info('gave ' + get_names_msg(message) + ' stats')
    elif message.text.lower() == 'топ':
        bot.send_message(message.chat.id, 'выбери, какой топ хочешь посмотреть', reply_markup=keyboard_choose_top)
    elif message.text.lower() == 'топ по рейтингу':
        ids.sort(key=comparator_rating, reverse=True)
        t = "*текущий топ\-10 по рейтингу:*\n"
        s = ""
        place = 0
        for i in range(10):
            if ids[i].banned == 1:
                continue
            if ids[i].top == 0:
                continue
            zvanie = ranks[min(len(ranks) - 1, place)]
            s += str(place + 1) + ") "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += "\| " + str(ids[i].rating) + " \| " + zvanie + "\n"
            place += 1
        s = replace_mark(s)
        bot.send_message(message.chat.id, t + s, reply_markup=keyboard_choose_top, parse_mode='MarkdownV2')

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' top_rating')
        logging.info('gave ' + get_names_msg(message) + ' top_rating')
    elif message.text.lower() == 'топ по стрику':
        ids.sort(key=comparator_streak, reverse=True)
        t = "*текущий топ\-10 по стрику:*\n"
        s = ""
        place = 0
        for i in range(10):
            if ids[i].banned == 1:
                continue
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
            s += "\| " + max_str + "\n"
            place += 1
        s = replace_mark(s)
        bot.send_message(message.chat.id, t + s, reply_markup=keyboard_choose_top, parse_mode='MarkdownV2')

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' top_streak')
        logging.info('gave ' + get_names_msg(message) + ' top_streak')
    elif message.text.lower() == 'топ по % правильных':
        ids.sort(key=comparator_percent, reverse=True)
        t = "*текущий топ\-10 по % правильных ответов* \(пользователи с количеством ответов не меньше 100\):\n"
        s = ""
        place = 0
        for i in range(10):
            if ids[i].top == 0 or ids[i].correct + ids[i].wrong < 100:
                continue
            if ids[i].banned == 1:
                continue
            s += str(place + 1) + ") "
            if str(ids[i].first_name) != "None":
                s += str(ids[i].first_name) + " "
            if str(ids[i].last_name) != "None":
                s += str(ids[i].last_name) + " "
            s += str(round(ids[i].correct / (ids[i].correct + ids[i].wrong) * 100.0, 2)) + "% (" + str(ids[i].correct) + " правильных из " + str(ids[i].wrong + ids[i].correct) + ")\n"
            place += 1
        s = replace_mark(s)
        bot.send_message(message.chat.id, t + s, reply_markup=keyboard_choose_top, parse_mode='MarkdownV2')

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' top_percent')
        logging.info('gave ' + get_names_msg(message) + ' top_percent')
    elif message.text.lower() == 'настройки' or message.text.lower() == 'вернуться к меню настроек':
        bot.send_message(message.chat.id, "да, настроек пока маловато... но это же лучше, чем ничего?", reply_markup=keyboard_settings)

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' settings_main')
        logging.info('gave ' + get_names_msg(message) + ' settings_main')
    elif message.text.lower() == 'сбросить прогресс':
        try:
            bot.send_message(message.chat.id, "ты ТОЧНО хочешь сбросить прогресс?\nВСЯ СТАТИСТИКА, ВСЕ ДОСТИЖЕНИЯ пропадут НАВСЕГДА и их НЕЛЬЗЯ будет вернуть", reply_markup=callback_buttons_loseprogress)
        except telebot.apihelper.ApiException:
            print(get_id(message.chat.id) + ' cant lose progress')
            logging.error(message.chat.id + ' cant lose progress')
    elif message.text.lower() == 'настройки уведомлений':
        try:
            bot.send_message(message.chat.id, 'вжух! и ты в настройках уведомлений!\nнапоминания - напоминалки о том, что стоит поботать.\nоповещения - различные новости о боте.',
                             reply_markup=keyboard_notification_settings)
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'выкл. напоминания':
        ind = get_id(message.chat.id)
        ids[ind].notify_game = 0
        upd_b()
        try:
            bot.send_message(message.chat.id, 'а как ботать?',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned off not_game')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned off not_game')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'вкл. напоминания':
        ind = get_id(message.chat.id)
        ids[ind].notify_game = 1
        upd_b()
        try:
            bot.send_message(message.chat.id, 'ночью не напишу, не беспокойся!',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned on not_game')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned on not_game')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'выкл. оповещения':
        ind = get_id(message.chat.id)
        ids[ind].notify_admin = 0
        upd_b()
        try:
            bot.send_message(message.chat.id, 'ну и ладно! ну и пожалуйста!',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned off not_adm')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned off not_adm')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'вкл. оповещения':
        ind = get_id(message.chat.id)
        ids[ind].notify_admin = 1
        upd_b()
        try:
            bot.send_message(message.chat.id, 'круто! посты разработчика реально крутые, на твоем месте я бы сделал так же!',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned on not_adm')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned on not_adm')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'выкл. все уведомления':
        ind = get_id(message.chat.id)
        ids[ind].notify_game = 0
        ids[ind].notify_admin = 0
        upd_b()
        try:
            bot.send_message(message.chat.id, 'так сразу?..',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned off not_all')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned off not_all')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'вкл. все уведомления':
        ind = get_id(message.chat.id)
        ids[ind].notify_game = 1
        ids[ind].notify_admin = 1
        upd_b()
        try:
            bot.send_message(message.chat.id, 'бодренько, товарищ!',
                             reply_markup=keyboard_notification_settings)
            logging.info(get_names_ind(ind) + ' turned on not_all')
            print(get_time() + ':: ' + get_names_ind(ind) + ' turned on not_all')
        except telebot.apihelper.ApiException:
            print('cant send message to ' + get_id(message.chat.id))
            logging.error('cant send message to ' + get_id(message.chat.id))
    elif message.text.lower() == 'настройки отображения в топе':
        bot.send_message(message.chat.id, "телепортирую в настройки отображения в топе...",
                         reply_markup=keyboard_top_settings)

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' settings_top')
        logging.info('gave ' + get_names_msg(message) + ' settings_top')
    elif message.text.lower() == 'вкл/выкл отображение в топе':
        bot.send_message(message.chat.id, "отображать ли тебя в топе?", reply_markup=callback_buttons_top)

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' settings_top_visibility')
        logging.info('gave ' + get_names_msg(message) + ' settings_top_visibility')
    elif message.text.lower() == 'обновить мое имя в топе':
        ind = get_id(message.chat.id)
        log_str = get_names_ind(ind) + ' changed name to '
        bot.send_message(message.chat.id, "изменил твое имя в соответствии с твоим телеграм-аккаунтом!")

        name = message.chat.first_name
        fam = message.chat.last_name
        if str(message.chat.first_name) != "None":
            name = name.replace(' ', '_')
        else:
            name = "None"
        if str(message.chat.last_name) != "None":
            fam = fam.replace(' ', '_')
        else:
            fam = "None"
        ids[ind].first_name = name
        ids[ind].last_name = fam

        log_str += get_names_ind(ind)

        print(get_time() + ':: ' + log_str)
        logging.info(log_str)
        upd_b()
    elif message.text.lower() == 'главное меню':
        bot.send_message(message.chat.id, "телепортируемся в главное меню!", reply_markup=keyboard_main)

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' main_menu')
        logging.info('gave ' + get_names_msg(message) + ' main_menu')
    elif message.text.lower() == 'достижения':
        ind = get_id(message.chat.id)
        text = "*достижения*🏆\n"
        for i in range(len(all_achievements)):
            if ids[ind].achievements[i] == 1:
                text += str(i + 1) + "\) " + all_achievements[i]
            else:
                text += str(i + 1) + "\) ~" + all_achievements[i] + "~"
            text += '\n'
        bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' achievements')
        logging.info('gave ' + get_names_msg(message) + ' achievements')
    elif message.text.lower() == 'слово!':
        ind_ids = get_id(message.chat.id)
        sum = get_sum(ind_ids)
        if sum == len(words):
            ids[ind_ids].used.clear()
            ids[ind_ids].used = [[0] * 2 for _ in range(len(words))]

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

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' word ' + words[word_ind])
        logging.info('gave ' + get_names_msg(message) + ' word ' + words[word_ind])
    elif message.text.lower() == 'помощь':
        bot.send_message(message.chat.id, "по всем вопросам/предложениям/советам/багам писать @Rustam_Fakhretdinov", reply_markup=keyboard_main)

        print(get_time() + ':: ' + 'gave ' + get_names_msg(message) + ' help')
        logging.info('gave ' + get_names_msg(message) + ' help')
    elif message.text.lower() == '444' and ids[ind].achievements[11] == 0:
        bot.send_message(chat_id=message.chat.id, text="получено достижение🏆\!\na big secret\!\n_so, why 444\?\.\._", parse_mode='MarkdownV2')
        ids[ind].achievements[11] = 1

        print(get_time() + ':: ' + get_names_msg(message) + ' got achievement 11')
        logging.info(get_names_msg(message) + ' got achievement 11')
        upd_b()
    else:
        bot.send_message(message.chat.id, "я, скорее всего, еще туповат, чтобы понять, что тут написано...", reply_markup=keyboard_main)


@bot.callback_query_handler(func=lambda call: True)  # реакция на callback кнопки
def callback_inline(call):
    if len(call.data) >= 4 and call.data[:4] == "good":
        ind = get_id(call.message.chat.id)
        if ids[ind].used[words.index(call.data[4:].lower())][0] > 1:
            r = 2
            ed_r = " единицы рейтинга"
        else:
            r = 1
            ed_r = " единицу рейтинга"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="правильно✅\nответ: " + link[call.data[4:].lower()] + "\nты получил " + str(r) + ed_r + '!')
        ids[ind].correct += 1
        ids[ind].last_answer = get_time_for_notif()
        ids[ind].skipped = 0
        ids[ind].used[words.index(call.data[4:].lower())][1] = 1
        ids[ind].rating += r
        if ids[ind].streak < 0:
            ids[ind].streak = 1
        else:
            ids[ind].streak += 1
        ids[ind].max_streak = max(ids[ind].max_streak, ids[ind].streak)

        print(get_time() + ':: ' + get_names_msg(call.message) + ' answered ' + call.data[4:].lower() + ' correct +' + str(r) + ' rating')
        logging.info(get_names_msg(call.message) + ' answered ' + link[call.data[4:].lower()].lower() + ' correct, +' + str(r) + ' rating')
        # achievements
        if get_sum(ind) == len(words) and ids[ind].achievements[0] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\nвсе слова были разблокированы!")
            ids[ind].achievements[0] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 0')
            logging.info(get_names_msg(call.message) + ' got achievement 0')
        if ids[ind].correct >= 100 and ids[ind].achievements[1] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n100 правильных слов!")
            ids[ind].achievements[1] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 1')
            logging.info(get_names_msg(call.message) + ' got achievement 1')
        if ids[ind].correct >= 500 and ids[ind].achievements[2] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n500 правильных слов!\nэто круто! продолжай в том же духе! =)")
            ids[ind].achievements[2] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 2')
            logging.info(get_names_msg(call.message) + ' got achievement 2')
        if ids[ind].correct >= 1000 and ids[ind].achievements[3] == 0:
            bot.send_message(chat_id=call.message.chat.id, text="получено достижение🏆!\n1000 правильных слов!\nэто очень много...")
            ids[ind].achievements[3] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 3')
            logging.info(get_names_msg(call.message) + ' got achievement 3')

        ids.sort(key=comparator_rating, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[4] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по рейтингу!\nты на вершине! поздравляю!")
            ids[ind].achievements[4] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 4')
            logging.info(get_names_msg(call.message) + ' got achievement 4')
        ids.sort(key=comparator_streak, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[5] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по стрику!\nты на вершине! поздравляю!")
            ids[ind].achievements[5] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 5')
            logging.info(get_names_msg(call.message) + ' got achievement 5')
        ids.sort(key=comparator_streak, reverse=True)
        ind = get_id(call.message.chat.id)
        if ind == 0 and ids[ind].achievements[6] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nтоп-1 по % правильных ответов!\nты на вершине! поздравляю!")
            ids[ind].achievements[6] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 6')
            logging.info(get_names_msg(call.message) + ' got achievement 6')

        if ids[ind].max_streak >= 10 and ids[ind].achievements[7] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 10!\nсильно. но можно сильнее.")
            ids[ind].achievements[7] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 7')
            logging.info(get_names_msg(call.message) + ' got achievement 7')
        if ids[ind].max_streak >= 50 and ids[ind].achievements[8] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 50!\nда ты в ударе🔥🔥🔥")
            ids[ind].achievements[8] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 8')
            logging.info(get_names_msg(call.message) + ' got achievement 8')
        if ids[ind].max_streak >= 100 and ids[ind].achievements[9] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 100!\nтакое реально вообще?! жесть...")
            ids[ind].achievements[9] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 9')
            logging.info(get_names_msg(call.message) + ' got achievement 9')
        if ids[ind].max_streak >= 250 and ids[ind].achievements[10] == 0:
            bot.send_message(chat_id=call.message.chat.id,
                             text="получено достижение🏆!\nстрик 250!\nпохоже, что ты всё выучил... поздравляю!")
            ids[ind].achievements[10] = 1

            print(get_time() + ':: ' + get_names_msg(call.message) + ' got achievement 10')
            logging.info(get_names_msg(call.message) + ' got achievement 10')
        upd_b()
    elif len(call.data) >= 3 and call.data[:3] == "bad":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="неправильно❌\nответ был: " + link[call.data[3:].lower()] + "\nты потерял 1 единицу рейтинга...")
        ind = get_id(call.message.chat.id)
        ids[ind].wrong += 1
        ids[ind].last_answer = get_time_for_notif()
        ids[ind].skipped = 0
        ids[ind].rating -= 1
        ids[ind].rating = max(ids[ind].rating, 0)
        if ids[ind].streak > 0:
            ids[ind].streak = -1
        else:
            ids[ind].streak -= 1

        print(get_time() + ':: ' + get_names_msg(call.message) + ' answered ' + call.data[3:].lower() + ' wrong, -1 rating')
        logging.info(get_names_msg(call.message) + ' answered ' + call.data[3:].lower() + ' wrong, -1 rating')
        upd_b()
    elif len(call.data) >= 7 and call.data[:7] == "top_yes":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="окей! надеюсь, ты сможешь покорить вершину!")
        ind = get_id(call.message.chat.id)

        print(get_time() + ':: ' + get_names_msg(call.message) + ' now available in top')
        logging.info(get_names_msg(call.message) + ' now available in top')
        ids[ind].top = 1
        upd_b()
    elif len(call.data) >= 6 and call.data[:6] == "top_no":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id,
                         text="хорошо, скрываю тебя")
        ind = get_id(call.message.chat.id)

        print(get_time() + ':: ' + get_names_msg(call.message) + ' now NOT available in top')
        logging.info(get_names_msg(call.message) + ' now NOT available in top')
        ids[ind].top = 0
        upd_b()
    elif call.data == "loseprog_yes":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="новая жизнь! новая жизнь!")
        lose_progress(call.message.chat.id)
        print(get_time() + ':: ' + get_names_msg(call.message) + ' lost all progress. hope he is ok...')
        logging.info(get_names_msg(call.message) + ' lost all progress. hope he is ok...')
        upd_b()
    elif call.data == "loseprog_no":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="никогда не сдавайся!")
        print(get_time() + ':: ' + get_names_msg(call.message) + ' made right decision')
        logging.info(get_names_msg(call.message) + ' made right decision')


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


def game_notification():
    nowtime = get_time_for_notif()
    for i in range(len(ids)):
        if ids[i].notify_game == 0 or ids[i].banned == 1:
            continue
        if nowtime - int(ids[i].last_answer) >= 15 and ids[i].skipped < 3:
            ids[i].skipped += 1
            try:
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! для тебя есть новое задание! если хочешь получить, жми на кнопку \"слово!\"\nвыключить такие уведомления можно в настройках.")
            except telebot.apihelper.ApiException:
                logging.error('cant send notification to ' + get_names_ind(i))

            print(get_time() + ':: ' + 'notification for ' + get_names_ind(i))
            logging.info('notification for ' + get_names_ind(i))
        elif 3 <= ids[i].skipped < 4 and nowtime - int(ids[i].last_answer) >= 15:
            ids[i].skipped += 1
            try:
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! давно тебя не было в уличных гонках! если хочешь получить вопросик, жми на кнопку \"слово!\"\nвыключить такие уведомления можно в настройках.")
            except telebot.apihelper.ApiException:
                logging.error('cant send notification to ' + get_names_ind(i))

            print(get_time() + ':: ' + 'notification for ' + get_names_ind(i))
            logging.info('notification for ' + get_names_ind(i))
        elif 4 <= ids[i].skipped < 5 and nowtime - int(ids[i].last_answer) >= 30:
            ids[i].skipped += 1
            try:
                bot.send_message(chat_id=ids[i].id,
                                 text="привет! последний раз предлагаю тебе вспомнить про ударения на егэ! если хочешь получить вопросик, жми на кнопку \"слово!\"\nвыключить такие уведомления можно в настройках.")
            except telebot.apihelper.ApiException:
                logging.error('cant send last notification to ' + get_names_ind(i))

            print(get_time() + ':: ' + 'LAST notification for ' + get_names_ind(i))
            logging.info('LAST notification for ' + get_names_ind(i))
    upd_b()


schedule.every().day.at("18:00").do(game_notification)


@multi_threading
def reminder():  # предложение ответить на вопрос каждые N единиц времени
    while True:
        schedule.run_pending()
        time.sleep(1)


setup()
reminder()
bot.polling(none_stop=True, interval=0)