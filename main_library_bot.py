from datetime import datetime
import os
from dateutil.relativedelta import relativedelta

import telebot
from telebot import types
import requests
from dotenv import load_dotenv

load_dotenv()
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(telegram_token)

# Dictionary to store user-specific data
user_data = {}

link = "http://127.0.0.1:8000/"


def create_buttons(markup):
    markup.add(types.InlineKeyboardButton("Borrow", callback_data="start_borrowing_process"))
    markup.add(types.InlineKeyboardButton("Return", callback_data="start_return_process"))
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Hi, {message.from_user.first_name} I'm a bot that will help you to borrow the book in our amazing library",
    )


@bot.message_handler(commands=["help"])
def help(message):
    markup = types.InlineKeyboardMarkup()
    user_id = message.chat.id
    if user_id not in user_data or not user_data[user_id].get('logged'):
        markup.add(types.InlineKeyboardButton("Login", callback_data="login"))
        markup.add(types.InlineKeyboardButton("Register", callback_data="register"))
    else:
        markup = create_buttons(markup)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


# Function to handle the callback query (Login Button)
@bot.callback_query_handler(func=lambda callback: callback.data == "login")
def login(callback):
    bot.send_message(callback.message.chat.id, "Input your email")
    user_data[callback.message.chat.id] = {'login': "yes"}
    bot.register_next_step_handler(callback.message, get_email)


@bot.callback_query_handler(func=lambda callback: callback.data == "register")
def register(callback):
    bot.send_message(callback.message.chat.id, "Input your email")
    user_data[callback.message.chat.id] = {'register': "yes"}
    bot.register_next_step_handler(callback.message, get_email)


# Function to get the email and proceed with password input
def get_email(message):
    email = message.text
    user_data[message.chat.id]["email"] = email
    bot.send_message(message.chat.id, "Input your password")
    bot.register_next_step_handler(message, get_password)


# Function to get the password and send a POST request to get the token
def get_password(message):
    user_id = message.chat.id
    password = message.text
    user_data[user_id]["password"] = password
    if user_data[user_id].get("login") is not None:
        login_finish(message)
    elif user_data[user_id].get("register") is not None:
        register_finish(message)


def login_finish(message):
    user_id = message.chat.id
    response = requests.post(
        url=f"{link}api/token/",
        json={"email": user_data[user_id]['email'], "password": user_data[user_id]["password"]},
    )

    if response.status_code == 200:
        token = response.json().get("access")
        headers = {"Authorization": f"Bearer {token}"}
        user_data[user_id] = {'logged': True, 'token': token, 'headers': headers}

        bot.send_message(message.chat.id, "Login was successful")
        requests.put(url=f"{link}chat_id/", json={"chat_id": message.chat.id}, headers=headers)

        markup = types.InlineKeyboardMarkup()
        markup = create_buttons(markup)
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)
    else:
        bot.send_message(
            message.chat.id,
            "Error while login, your login or password were not correct. Please try again.",
        )


def register_finish(message):
    user_id = message.chat.id
    response = requests.post(
        url=f"{link}register/",
        json={"email": user_data[user_id]['email'], "password": user_data[user_id]["password"]},
    )
    markup = types.InlineKeyboardMarkup()
    if response.status_code == 201:
        bot.send_message(message.chat.id, "You was registered successfully")
        markup.add(types.InlineKeyboardButton("Login", callback_data="login"))
    else:
        bot.send_message(
            message.chat.id,
            f"Error while registration:\n{response.json()['email'][0]}\n{response.json()['password'][0]}",
        )
        markup.add(types.InlineKeyboardButton("Register", callback_data="register"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


# Handle other callback queries for additional buttons after login
@bot.callback_query_handler(
    func=lambda callback: callback.data == "start_borrowing_process"
)
def handle_borrowing_start(callback):
    all_books = \
        requests.get(url=f"{link}api/book_service/books/",
                     headers=user_data[callback.message.chat.id]['headers']).json()[
            "results"]
    all_authors = "All authors:\n"
    i = 1
    for book in all_books:
        all_authors += f"{i}. {book['author']}\n"
        i += 1
    all_authors.rstrip()
    bot.send_message(callback.message.chat.id, all_authors)
    bot.send_message(callback.message.chat.id, "Write the author whose book you want to borrow")
    bot.register_next_step_handler(callback.message, get_author)


def get_author(message):
    user_id = message.chat.id
    author = message.text.strip()
    headers = user_data[user_id]['headers']
    all_books = requests.get(url=f"{link}api/book_service/books/", headers=headers).json()["results"]
    author_books = []
    markup = types.InlineKeyboardMarkup()
    for book in all_books:
        if book["author"].lower() == author.lower():
            author_books.append(book)
            markup.add(types.InlineKeyboardButton(f"{book['title']}", callback_data=f"borrow {book['id']}"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


@bot.callback_query_handler(
    func=lambda callback: callback.data.startswith("borrow")
)
def handle_borrowing_finish(callback):
    user_id = callback.message.chat.id
    id = callback.data.split()[1]
    today = datetime.today()
    one_month_later = today + relativedelta(months=1)
    headers = user_data[user_id]['headers']
    response = requests.post(f"{link}api/borrowing_service/borrow/", json={
        "borrow_date": today.strftime("%Y-%m-%d"),
        "expected_return": one_month_later.strftime("%Y-%m-%d"),
        "actual_return": None,
        "book": id
    }, headers=headers)
    if response.status_code != 201:
        bot.send_message(callback.message.chat.id,
                         "Sorry, I couldn't borrow the book. It seems that no books left on stock")


@bot.callback_query_handler(
    func=lambda callback: callback.data == "start_return_process"
)
def handle_return_start(callback):
    all_active_borrowings_list = \
        requests.get(url=f"{link}api/borrowing_service/return/",
                     headers=user_data[callback.message.chat.id]['headers']).json()["data"]
    all_active_borrowings_str = "All active borrowings:\n"
    for borrowing in all_active_borrowings_list:
        all_active_borrowings_str += f"id: {borrowing['id']}, date: {borrowing['expected_return']}\n"
    all_active_borrowings_str.rstrip()
    bot.send_message(callback.message.chat.id, all_active_borrowings_str)
    bot.send_message(callback.message.chat.id, "Write the id of borrowing which you want to return")
    bot.register_next_step_handler(callback.message, return_book)


def return_book(message):
    borrowing_id = message.text.strip()
    response = requests.post(url=f"{link}api/borrowing_service/return/",
                             headers=user_data[message.chat.id]['headers'],
                             json={"borrowing_id": borrowing_id}
                             )
    if response.status_code == 200:
        bot.send_message(message.chat.id, "You returned the book")
    else:
        bot.send_message(message.chat.id, "Sorry, I couldn't returned the book, it seems that you input the wrong id.")


bot.polling(none_stop=True)
