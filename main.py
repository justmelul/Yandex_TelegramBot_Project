import telebot
import config
from telebot import types

# беру токен бота из файла config
bot = telebot.TeleBot(config.token)


# таблица id - таблица id книги id user название книги

# при команде /start вызывается эта часть кода
@bot.message_handler(commands=['start'])
def welcome(message):
    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()

    # если нет записи  о пользователе в бд, создаем запись
    if not cur.execute("""SELECT id FROM name WHERE id = ?""", (message.from_user.id,)).fetchall():
        # создаем запись в бд с новым ид
        cur.execute("""INSERT INTO name(username, id) VALUES(?, ?)""",
                    (message.from_user.first_name, message.from_user.id,))

    con.commit()
    cur.close()

    # создаем кнопки для управления
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("список 'мои желания'")
    item2 = types.KeyboardButton("добавить книгу в 'мои желания' (/add)")
    item3 = types.KeyboardButton("удалить книгу из 'мои желания' (/del)")
    item4 = types.KeyboardButton("удалить все записи из 'мои желания' (или /all)")
    item5 = types.KeyboardButton("я - Админ (/admin)")

    # добавляем кнопки
    markup.add(item1, item2, item3, item4, item5)

    # приветственное сообщение
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот книжного магазина в котором можно редактировать список 'мои желания'.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)
    #


# при команде /add вызывается эта часть кода
@bot.message_handler(commands=['add'])
def add_to_fav(message):
    # title -- текст написаный пользователем посе /add
    title = ' '.join(str(message.text).split()[1:])

    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()

    # if будет действовать если название книги не равно ''
    if title != '':

        # for нужен для того что-бы понять, есть-ли записи о пользователе в бд
        for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
            # если запись есть
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()

            if str(i[0]) != 'None':
                viv = str(i[0]) + f';{title}'
                bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
                cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (viv, message.from_user.id,))

            # если записи о пользователе нет
            else:
                viv = f'{title}'
                bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
                cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (viv, message.from_user.id,))

            con.commit()
            cur.close()
    con.commit()
    cur.close()


# при команде /del вызывается эта часть кода
@bot.message_handler(commands=['del'])
def del_from_fav(message):
    title = ' '.join(str(message.text).split()[1:])

    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
        viv = i[0].split(';')
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()

        if len(viv) == 1:
            viv.clear()
            bot.send_message(message.chat.id, 'список пуст')
            cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (None, message.from_user.id,))

        else:
            del viv[viv.index(title)]
            viv = ';'.join(viv)
            bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
            cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (viv, message.from_user.id,))

        con.commit()
        cur.close()


# удалить все записи из 'мои желания' (или /all)
@bot.message_handler(commands=['all'])
def del_all(message_):
    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (None, message_.from_user.id,))
    bot.send_message(message_.chat.id, 'список пуст')
    con.commit()
    cur.close()


# я - Админ (/admin)
# что-бы стать админом
@bot.message_handler(commands=['admin'])
def admin(message):
    title = ' '.join(str(message.text).split()[1:])

    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    for i in cur.execute("""SELECT admin_status FROM name WHERE id = ?""", (message.from_user.id,)):
        temp = i[0]
    cur.close()

    # если admin_status не True
    if not temp:

        # если пароль подходит
        if config.password == title:

            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            cur.execute("""UPDATE name SET admin_status = ? WHERE id = ?""", ('True', message.from_user.id,))
            con.commit()
            cur.close()

            bot.send_message(message.chat.id, 'вы админ')

            # создаем кнопки для управления
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item_1 = types.KeyboardButton("список всех пользователей")
            item_2 = types.KeyboardButton("список всех книг пользователей (могут повторяться)")
            item_3 = types.KeyboardButton("удалить все записи пользователей")

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("список 'мои желания'")
            item2 = types.KeyboardButton("добавить книгу в 'мои желания' (/add)")
            item3 = types.KeyboardButton("удалить книгу из 'мои желания' (/del)")
            item4 = types.KeyboardButton("удалить все записи из 'мои желания' (или /all)")

            # добавляем кнопки
            markup.add(item1, item2, item3, item4, item_1, item_2, item_3)

            bot.send_message(message.chat.id,
                             "Добро пожаловать, {0.first_name}, теперь вы админ на этом сервере по маинкрафту".format(
                                 message.from_user), parse_mode='html', reply_markup=markup)



        # если пароль не подходит
        else:
            bot.send_message(message.chat.id, 'неправильный пароль')

    else:
        bot.send_message(message.chat.id, 'вы админ')

        # создаем кнопки для управления

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton("список всех пользователей")
        item_2 = types.KeyboardButton("список всех книг пользователей (могут повторяться)")
        item_3 = types.KeyboardButton("удалить все записи пользователей")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("список 'мои желания'")
        item2 = types.KeyboardButton("добавить книгу в 'мои желания' (/add)")
        item3 = types.KeyboardButton("удалить книгу из 'мои желания' (/del)")
        item4 = types.KeyboardButton("удалить все записи из 'мои желания' (или /all)")

        # добавляем кнопки
        markup.add(item1, item2, item3, item4, item_1, item_2, item_3)

        bot.send_message(message.chat.id,
                         "Добро пожаловать, {0.first_name}, теперь вы админ на этом сервере по маинкрафту".format(
                             message.from_user), parse_mode='html', reply_markup=markup)


# если пользователь отправил текст :
@bot.message_handler(content_types=['text'])
def when_text(message):
    if message.chat.type == 'private':

        import sqlite3
        con = sqlite3.connect("database.sqlite")
        cur = con.cursor()
        temp = ''

        for i in cur.execute("""SELECT admin_status FROM name WHERE id = ?""", (message.from_user.id,)):
            temp = i[0]
        cur.close()

        if message.text == "список 'мои желания'":

            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
                if i[0] == '' or str(i[0]) == 'None':
                    bot.send_message(message.chat.id, 'список пуст')
                else:
                    bot.send_message(message.chat.id, ' | '.join(str(i[0]).split(';')))
            con.close()

        elif message.text == "добавить книгу в 'мои желания' (/add)":
            bot.send_message(message.chat.id,
                             'что-бы добавить книгу в мои желания использйте команду "/add (введите название книги)"')
        elif message.text == "удалить книгу из 'мои желания' (/del)":
            bot.send_message(message.chat.id,
                             'что-бы удалить книгу из мои желания использйте команду "/del (введите название книги)"')

        elif message.text == "я - Админ (/admin)":
            bot.send_message(message.chat.id, 'если вы админ /admin (пароль из файла config)')

        elif message.text == "удалить все записи из 'мои желания' (или /all)":
            bot.send_message(message.chat.id, 'что-бы удалить все книги из "мои желания" использйте команду "/all"')

        # только для админов
        # список всех пользователей

        elif message.text == "список всех пользователей" and temp == 'True':
            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()

            spis = []
            for i in cur.execute("""SELECT username FROM name"""):
                spis.append(i[0])
            viv = ' | '.join(spis)
            bot.send_message(message.chat.id, viv)
            con.close()

        # список всех книг пользователей (могут повторяться)

        elif message.text == "список всех книг пользователей (могут повторяться)" and temp == 'True':
            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()

            spis = []
            for i in cur.execute("""SELECT favorites FROM name"""):
                spis.append(i[0])

            razdelenie = ''
            for i in spis:
                razdelenie += ' || '
                razdelenie += ' | '.join(str(i).split(';'))

            bot.send_message(message.chat.id, razdelenie)
            con.close()

        # удалить все записи пользователей

        elif message.text == "удалить все записи пользователей" and temp == 'True':

            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()

            cur.execute("""UPDATE name SET favorites = ?""", ('',))

            con.commit()
            cur.close()

            bot.send_message(message.chat.id, 'записи удалены')

        #
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить')


# RUN
bot.polling(none_stop=True)
