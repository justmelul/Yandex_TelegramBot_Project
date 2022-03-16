import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("список 'мои желания'")
    item2 = types.KeyboardButton("добавить книгу в 'мои желания' (/add)")
    item3 = types.KeyboardButton("удалить книгу из 'мои желания' (/del)")

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>, бот книжного магазина в котором можно редактировать список 'мои желания'.".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['add'])
def addtofav(message):
    title = ' '.join(str(message.text).split()[1:])

    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
        if str(i[0]) != '':
            viv = str(i[0]) + f';{title}'
            bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
        else:
            viv = f'{title}'
            bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
    con.close()

    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (viv, message.from_user.id,))
    con.commit()
    cur.close()


@bot.message_handler(commands=['del'])
def delfromfav(message):
    title = ' '.join(str(message.text).split()[1:])

    import sqlite3
    con = sqlite3.connect("database.sqlite")
    cur = con.cursor()
    for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
        print(i[0])
        viv = i[0].split(';')
        if len(viv) == 1:
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            viv.clear()
            bot.send_message(message.chat.id, 'список пуст')
            con.close()

            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", ('', message.from_user.id,))

            con.commit()
            cur.close()

        else:
            del viv[viv.index(title)]
            viv = ';'.join(viv)
            bot.send_message(message.chat.id, ' | '.join(viv.split(';')))
            con.close()

            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            cur.execute("""UPDATE name SET favorites = ? WHERE id = ?""", (viv, message.from_user.id,))

            con.commit()
            cur.close()


@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == "список 'мои желания'":

            import sqlite3
            con = sqlite3.connect("database.sqlite")
            cur = con.cursor()
            for i in cur.execute("""SELECT favorites FROM name WHERE id = ?""", (message.from_user.id,)):
                if i[0] == '':
                    bot.send_message(message.chat.id, 'список пуст')
                else:
                    bot.send_message(message.chat.id, ' | '.join(str(i[0]).split(';')))
            con.close()

        elif message.text == "добавить книгу в 'мои желания' (/add)":
            bot.send_message(message.chat.id,
                             'что-бы добавить книгу в мои желания использйте команду "/add (введите название книги)"')
        elif message.text == "удалить книгу из 'мои желания' (/del)":
            bot.send_message(message.chat.id,
                             'что-бы удаить книгу из мои желания использйте команду "/del (введите название книги)"')
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить')


# RUN
bot.polling(none_stop=True)
