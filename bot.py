from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import openai
from config import TOKEN
import mysql.connector
import random
#доб  библиотеку переводчика
from yandexfreetranslate import YandexFreeTranslate
yt = YandexFreeTranslate()
yt = YandexFreeTranslate(api = "ios")

# mysql соед...
mydb = mysql.connector.connect(
  host="localhost",
  user="admin",
  password="firdavs2001",
  database="bot_data"
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

    keyboard.add(button1, button2, button3)

    await bot.send_message(message.chat.id, "Выберите язык, на котором хотите задать свой вопрос:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["tg", "ru", "en"])
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
    keyboard.add(button1, button2, button3)
    await bot.send_message(message.chat.id, "На каком языке хотите получить ответ:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["tg_q", "ru_q", "en_q"])
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
    mycursor = mydb.cursor()
    sql = "INSERT INTO language2(user_telegram_id, q_lang, a_lang) VALUES (%s, %s, %s)"
    val = (user_id, first_answer, second_answer)
    mycursor.execute(sql, val)
    mydb.commit()
    query = "SELECT q_lang, a_lang FROM language2 WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
    mycursor.execute(query, (user_id,))
    results = mycursor.fetchall()
    q_lang = (results[0][0])
    a_lang = (results[0][1])


    if q_lang == "tg":
    	lang = "Тоҷикӣ"
    elif q_lang == "en":
    	lang = "Engish"
    else : 
    	lang = "Русский"
    
    if a_lang == "tg":
    	alang = "Тоҷикӣ"
    elif a_lang == "en":
    	alang = "Engish"
    else : 
    	alang = "Русский"
    
    await bot.send_message(callback_query.message.chat.id, f"Вопрос на языке: {lang}\n Ответ на языке:{alang}")



@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")
    print(first_answer)





@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
   if msg.from_user.first_name == "O":
       await msg.answer('У вас закончились токены, попробуйте завтра')

   elif msg.text.lower() == 'пидораз' or msg.text.lower() == "пидараз" or msg.text.lower()=="пидараз":
       await msg.answer('Сам такой!')
   elif msg.text.lower() == 'привет' or msg.text.lower() == "салом":
       await msg.answer('Привет!')
   else:
       user_id = msg.from_user.id


       whate = "⌛ Пожалуйста, подождите "
       sent_message = await bot.send_message(msg.from_user.id, whate)
       openai_api_keys = ["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", "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", "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", "SP40YsBn4gYprGndso80T3BlbkFJ91E1q3lInHdhVd7hEEih", "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"]
       openai.api_key = random.choice(openai_api_keys)
       model_engine = "text-davinci-003" #"text-davinci-003"

       mycursor = mydb.cursor()
       query = "SELECT q_lang, a_lang FROM language2 WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
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

       if len(prompt) > 200:
           await msg.answer('слишком длинный вопрос!')

       # генерируем ответ
       completion = openai.Completion.create(
           engine=model_engine,
           prompt=prompt,
           max_tokens=590,
           temperature=0.5,
           top_p=1,
           frequency_penalty=0,
           presence_penalty=0
       )
       #бот выдает ответ
       # print(second_answer)
       query = "SELECT q_lang, a_lang FROM language2 WHERE user_telegram_id = %s ORDER BY id DESC LIMIT 1"
       mycursor.execute(query, (user_id,))
       results = mycursor.fetchall()

       if len(results) == 0:
           a_lang = "ru"
       else:
           a_lang = (results[0][1])
       from datetime import datetime
       current_dateTime = datetime.now()
       print(user_id, "язык ответа:", a_lang,"| дата: ",current_dateTime.year,".",current_dateTime.month,".",current_dateTime.day, current_dateTime.hour,":",current_dateTime.minute)
       if a_lang in ["tg","en"]:
           text_ot = yt.translate("ru", a_lang, completion.choices[0].text)
           await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
           await bot.send_message(msg.from_user.id, text_ot)
       else:
           await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
           await bot.send_message(msg.from_user.id, completion.choices[0].text)



       #print(completion.choices[0].text)
       mycursor = mydb.cursor()
       sql = "INSERT INTO bot_history2 (user_first_name, user_last_name, username, question, answer) VALUES (%s, %s, %s, %s, %s)"
       val = (msg.from_user.first_name, msg.from_user.last_name, msg.from_user.username, msg.text, completion.choices[0].text)
       mycursor.execute(sql, val)
       mydb.commit()

if __name__ == '__main__':
    executor.start_polling(dp)

