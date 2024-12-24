import os

import telebot
from telebot import types
import requests
from dotenv import load_dotenv
telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot("token")
logged = False
token = ""
headers = {"Authorize": f"Bearer {token}"}


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Hi,{message.from_user.first_name} I'm a bot that will help you to borrow the book in our amazing library",
    )


@bot.message_handler(commands=["help"])
def help(message):
    markup = types.InlineKeyboardMarkup()
    if not logged:
        markup.add(types.InlineKeyboardButton("Login", callback_data="login"))
    else:
        markup.add(types.InlineKeyboardButton("Option 1", callback_data="option1"))
        markup.add(types.InlineKeyboardButton("Option 2", callback_data="option2"))
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


# Function to handle the callback query (Login Button)
@bot.callback_query_handler(func=lambda callback: True)
def callback_query(callback):
    global token
    if callback.data == "login":
        bot.send_message(callback.message.chat.id, "Input your email")
        bot.register_next_step_handler(callback.message, get_email)


# Function to get the email and proceed with password input
def get_email(message):
    email = message.text
    bot.send_message(message.chat.id, "Input your password")
    bot.register_next_step_handler(message, get_password, email)


# Function to get the password and send a POST request to get the token
def get_password(message, email):
    password = message.text
    # POST request to get the token
    response = requests.post(
        url="http://127.0.0.1:8000/api/token/",  # Correct the URL
        json={"email": email, "password": password},  # Use json instead of data
    )

    if response.status_code == 200:
        global token
        global logged
        token = response.json().get("access")


        bot.send_message(message.chat.id, "Login was successful")
        logged = True
        # After login, show additional buttons
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Option 1", callback_data="option1"))
        markup.add(types.InlineKeyboardButton("Option 2", callback_data="option2"))
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

    else:
        bot.send_message(
            message.chat.id,
            "Error while login, your login or password were not correct. Please try again.",
        )


# Handle other callback queries for additional buttons after login
@bot.callback_query_handler(
    func=lambda callback: callback.data in ["option1", "option2"]
)
def handle_additional_buttons(callback):
    if callback.data == "option1":
        bot.send_message(callback.message.chat.id, "You selected Option 1.")
    elif callback.data == "option2":
        bot.send_message(callback.message.chat.id, "You selected Option 2.")


bot.polling(none_stop=True)
