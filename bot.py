from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import openai
from config import TOKEN
import mysql.connector

#доб  библиотеку переводчика
from yandexfreetranslate import YandexFreeTranslate
yt = YandexFreeTranslate()

# mysql соед...
mydb = mysql.connector.connect(
  host="localhost",
  user="bot_user",
  password="123",
  database="bot"
)
# openai.api_key = "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"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет, я теперь могу понимать и отвечать на таджикском и узбекском языках. "
                        "Вы можете задавать мне вопросы на одном из этих языков, а я буду отвечать)")
    user_id = message.from_user.username


    await message.reply("Чтобы выбрать языки, на которм будете задавать вопросы и хотите получать ответы, введите /lang\nПо умолчанию, можно задавать вопросы на русском и английких языках.")


@dp.message_handler(commands=['lang'])
async def ask_first_question(message):
    global user_id 
    user_id = message.from_user.id
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Тоҷикӣ", callback_data="tg")
    button2 = InlineKeyboardButton("Русский", callback_data="ru")
    button3 = InlineKeyboardButton("English", callback_data="en")
    button4 = InlineKeyboardButton("O'zbek", callback_data="uz")
    keyboard.add(button1, button2, button3, button4)

    await bot.send_message(message.chat.id, "Выберите язык, на котором хотите задать свой вопрос:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["tg", "ru", "en", "uz"])
async def process_first_answer(callback_query):
    global first_answer
    first_answer = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    await ask_second_question(callback_query.message)
async def ask_second_question(message):

    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton("Русский ", callback_data="ru_q")
    button2 = InlineKeyboardButton("Тоҷикӣ", callback_data="tg_q")
    button3 = InlineKeyboardButton("English", callback_data="en_q")
    button4 = InlineKeyboardButton("O`zbek", callback_data="uz_q")
    keyboard.add(button1, button2, button3, button4)
    await bot.send_message(message.chat.id, "На коком языке хотите получить ответ:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["tg_q", "ru_q", "en_q", "uz_q"])
async def process_second_answer(callback_query):
    global second_answer
    second_answer = callback_query.data
    await bot.answer_callback_query(callback_query.id)
    if second_answer == "tg_q":
        second_answer = "tg"
    elif second_answer == "ru_q":
        second_answer = "ru"
    elif second_answer == "en_q":
        second_answer = "en"
    elif second_answer == "uz_q":
        second_answer = "uz"
    # if second_answer == "tg":
    #     second_answer = "tj"
    mycursor = mydb.cursor()
    sql = "INSERT INTO language(user_telegram_id, q_lang, a_lang) VALUES (%s, %s, %s)"
    val = (user_id, first_answer, second_answer)
    mycursor.execute(sql, val)
    mydb.commit()
    query = "SELECT q_lang, a_lang FROM language WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
    mycursor.execute(query, (user_id,))
    results = mycursor.fetchall()
    q_lang = (results[0][0])
    a_lang = (results[0][1])




    await bot.send_message(callback_query.message.chat.id, f"Вопрос на языке: {q_lang}\n Ответ на языке:{a_lang}")



@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
    print(first_answer)





@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):


   if msg.text.lower() == 'привет':
       await msg.answer('Привет!')


   else:
       user_id = msg.from_user.id
       whate = "⌛ Пожалуйста, подождите "
       await bot.send_message(msg.from_user.id, whate)
       openai.api_key = "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"
       model_engine = "text-davinci-003"

       mycursor = mydb.cursor()
       query = "SELECT q_lang, a_lang FROM language WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
       user_id = msg.from_user.id

       mycursor.execute(query, (user_id,))
       results = mycursor.fetchall()
       if len(results) == 0:
           q_lang = "ru"
       else:
           q_lang = (results[0][0])
       print(user_id, "язык вопроса:", q_lang,)
       if q_lang in ["tg", "uz"]:
           text_ya = yt.translate(q_lang, "ru", msg.text)
           prompt = text_ya          #msg.text
       else:
           prompt=msg.text


       # генерируем ответ
       completion = openai.Completion.create(
           engine=model_engine,
           prompt=prompt,
           max_tokens=1024,
           temperature=0.5,
           top_p=1,
           frequency_penalty=0,
           presence_penalty=0
       )
       #бот выдает ответ
       # print(second_answer)
       query = "SELECT q_lang, a_lang FROM language WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
       mycursor.execute(query, (user_id,))
       results = mycursor.fetchall()

       if len(results) == 0:
           a_lang = "ru"
       else:
           a_lang = (results[0][1])
       from datetime import datetime
       current_dateTime = datetime.now()
       print(user_id, "язык ответа:", a_lang,"| дата: ",current_dateTime.year,".",current_dateTime.month,".",current_dateTime.day, current_dateTime.hour,":",current_dateTime.minute)
       if a_lang in ["tg", "uz", "en"]:
           text_ot = yt.translate("ru", a_lang, completion.choices[0].text)
           await bot.send_message(msg.from_user.id, text_ot)
       else:
           await bot.send_message(msg.from_user.id, completion.choices[0].text)



       #print(completion.choices[0].text)
       mycursor = mydb.cursor()
       sql = "INSERT INTO bots_data (user_first_name, user_last_name, username, question, answer) VALUES (%s, %s, %s, %s, %s)"
       val = (msg.from_user.first_name, msg.from_user.last_name, msg.from_user.username, msg.text, completion.choices[0].text)
       mycursor.execute(sql, val)
       mydb.commit()

if __name__ == '__main__':
    executor.start_polling(dp)

#await bot.send_message(msg.from_user.id, msg.text )
