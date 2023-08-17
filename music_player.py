import telebot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import configparser
from telebot import types

# Load configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

bot = telebot.TeleBot(config['BOT']['token'])

# تنظیمات API Spotify
spotify_client_id = '1f435cc9c6d943dfa04c4c83ed8830db'
spotify_client_secret = '554c89c385fb4d5ab0f62eedec2e82af'
spotify_credentials = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
spotify = spotipy.Spotify(client_credentials_manager=spotify_credentials)

# first_button = types.InlineKeyboardButton("👤 درباره ما", callback_data="num 1")
second_button = types.InlineKeyboardButton("ارتباط با ما", url="https://t.me/alireza18z31")
markup = types.InlineKeyboardMarkup()
markup.add(second_button)

# @bot.callback_query_handler(func=lambda call: True)
# def callback(call):
#     if call.data == "num 1":
#         bot.answer_callback_query(call.id, 'ما یک شرکت فناوری هستیم که در زمینه توسعه ربات‌های تلگرامی فعالیت می‌کنیم.', show_alert=True)

# ایجاد دکمه‌های شخصی‌سازی شده
key_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
itembtn1 = types.KeyboardButton('جستجوی موزیک')
itembtn2 = types.KeyboardButton('👤 درباره ما')
key_markup.add(itembtn1, itembtn2)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,  "سلام! به ربات music Z خوش اومدی. برای پیدا کردن آهنگ کلید جست و جوی موزیک رو بزن یا از دستور /play استفاده کن.", reply_markup=key_markup)

# پاسخ به دکمه درباره ما
@bot.message_handler(func=lambda m: m.text == '👤 درباره ما')
def about_us(message):
    bot.send_message(message.chat.id, "سلام! من muzic.Z هستم. من یک ربات تلگرام هستم که امکاناتی را برای پیدا کردن موزیک ارائه می‌دهم. من توسط Alireza.Z توسعه داده شده‌ام و آماده‌ام تا به شما کمک کنم." , reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == 'جستجوی موزیک')
def music(message):
    handle_play_command(message)

# تابع برای جستجوی اهنگ در Spotify
def search_song_on_spotify(song_name):
    query = 'track:' + song_name
    search_result = spotify.search(query, type='track', limit=5)  # افزایش محدودیت تعداد نتایج جستجو
    tracks = search_result['tracks']['items']
    if len(tracks) == 0:
        return None
    else:
        song_info_list = []
        for track_info in tracks:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']
            track_id = track_info['id']  # اضافه کردن دریافت شناسه آهنگ
            track_info = spotify.track(track_id)  # دریافت اطلاعات کامل آهنگ
            track_preview_url = track_info['preview_url']
            track_cover_url = track_info['album']['images'][0]['url']
            song_info = {'name': track_name, 'artist': track_artist, 'preview_url': track_preview_url, 'cover_url': track_cover_url}
            song_info_list.append(song_info)
        return song_info_list


# تابع برای پخش اهنگ با استفاده از URL پیش‌نمایش اهنگ
def play_song_from_url(chat_id, song_info):
    for song in song_info:
        audio_caption = f'نام اهنگ: {song["name"]}\nنام خواننده: {song["artist"]}'
        audio_file = requests.get(song['preview_url']).content
        audio_cover = requests.get(song['cover_url']).content
        # جایگزینی send_audio به send_audio_chat_action
        bot.send_chat_action(chat_id, 'upload_audio')
        # ارسال نسخه کامل موزیک
        bot.send_audio(chat_id=chat_id, audio=audio_file, caption=audio_caption, performer=song['artist'], title=song['name'], thumb=audio_cover)


# پاسخ به دستور /play
@bot.message_handler(commands=['play'])
def handle_play_command(message):
    bot.send_message(message.chat.id, "نام آهنگ موردنظر را وارد کنید:")
    bot.register_next_step_handler(message, process_song_name)

def process_song_name(message):
    song_name = message.text
    song_info = search_song_on_spotify(song_name)
    if song_info is None:
        bot.send_message(message.chat.id, 'هیچ اهنگی با این نام پیدا نشد.')
    else:
        play_song_from_url(message.chat.id, song_info)

# شروع گوش دادن به ورودی‌های ربات
bot.polling(none_stop=True,interval=0)