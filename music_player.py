import telebot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import configparser
from telebot import types
from search_with_artist import *

a = 0

# Load configuration from the config.ini file
config = configparser.ConfigParser()
config.read("config.ini")

bot = telebot.TeleBot(config["BOT"]["token"])

# تنظیمات API Spotify
spotify_client_id = config["SPOTIFY"]["spotify_client_id"]
spotify_client_secret = config["SPOTIFY"]["spotify_client_secret"]
spotify_credentials = SpotifyClientCredentials(
    client_id=spotify_client_id, client_secret=spotify_client_secret
)
spotify = spotipy.Spotify(client_credentials_manager=spotify_credentials)

first_button = types.InlineKeyboardButton(
    "ارتباط با ما", url="https://t.me/alireza18z31"
)
markup = types.InlineKeyboardMarkup()
markup.add(first_button)


# ایجاد دکمه‌های شخصی‌سازی شده
key_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton("جستجوی موزیک")
itembtn2 = types.KeyboardButton("👤 درباره ما")
itembtn3 = types.KeyboardButton("جستجوی موزیک بااسم اهنگ و خواننده")
key_markup.add(itembtn1, itembtn2, itembtn3)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "سلام! به ربات music Z خوش اومدی. برای پیدا کردن آهنگ کلید جست و جوی موزیک رو بزن یا از دستور /play استفاده کن.",
        reply_markup=key_markup,
    )


# پاسخ به دکمه درباره ما
@bot.message_handler(func=lambda m: m.text == "👤 درباره ما")
def about_us(message):
    bot.send_message(
        message.chat.id,
        "سلام! من muzic.Z هستم. من یک ربات تلگرام هستم که امکاناتی را برای پیدا کردن موزیک ارائه می‌دهم. من توسط Alireza.Z توسعه داده شده‌ام و آماده‌ام تا به شما کمک کنم.",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda m: m.text == "جستجوی موزیک")
def music(message):
    handle_play_command(message)


@bot.message_handler(func=lambda m: m.text == "جستجوی موزیک بااسم اهنگ و خواننده")
def music(message):
    global a
    a = 1
    handle_play_command(message)


# تابع برای پخش اهنگ با استفاده از URL پیش‌نمایش اهنگ
def play_song_from_url(chat_id, song_info):
    for song in song_info:
        if song["preview_url"] is None:
            bot.send_message(chat_id, "پیش‌نمایش برای این آهنگ در دسترس نیست.")
        else:
            audio_caption = f'نام اهنگ: {song["name"]}\nنام خواننده: {song["artist"]}'
            audio_file = requests.get(song["preview_url"]).content
            audio_cover = requests.get(song["cover_url"]).content
            # جایگزینی send_audio به send_audio_chat_action
            bot.send_chat_action(chat_id, "upload_audio")
            # ارسال نسخه کامل موزیک
            bot.send_audio(
                chat_id=chat_id,
                audio=audio_file,
                caption=audio_caption,
                performer=song["artist"],
                title=song["name"],
                thumb=audio_cover,
            )


# پاسخ به دستور /play
@bot.message_handler(commands=["play"])
def handle_play_command(message):
    global a
    bot.send_message(message.chat.id, "نام آهنگ موردنظر را وارد کنید:")
    if a != 1:
        bot.register_next_step_handler(message, process_song_name)
    elif a == 1:
        bot.register_next_step_handler(message, process_song_name_2)
        a = 0


def process_song_name_2(message):
    song_name = message.text
    bot.send_message(message.chat.id, "نام خواننده را به صورت کامل وارد کنید:")
    bot.register_next_step_handler(
        message, lambda msg: process_song_artist(msg, song_name)
    )


def process_song_artist(message, song_name):
    artist_name = message.text
    song_info = search_song_on_spotify_2(song_name, artist_name)
    if song_info is None:
        bot.send_message(message.chat.id, "هیچ اهنگی با این نام و خواننده پیدا نشد.")
    else:
        play_song_from_url(message.chat.id, song_info)


def process_song_name(message):
    song_name = message.text
    song_info = search_song_on_spotify(song_name)
    if song_info is None:
        bot.send_message(message.chat.id, "هیچ اهنگی با این نام پیدا نشد.")
    else:
        play_song_from_url(message.chat.id, song_info)


bot.polling(none_stop=True, interval=0)
