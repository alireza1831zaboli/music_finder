# تابع برای جستجوی اهنگ در Spotify بر اساس نام آهنگ و خواننده
import telebot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

bot = telebot.TeleBot(config['BOT']['token'])

# تنظیمات API Spotify
spotify_client_id = config['SPOTIFY']['spotify_client_id']
spotify_client_secret = config['SPOTIFY']['spotify_client_secret']
spotify_credentials = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
spotify = spotipy.Spotify(client_credentials_manager=spotify_credentials)


def search_song_on_spotify_2(song_name, artist_name):
    query = f'track:{song_name} artist:{artist_name}'
    search_result = spotify.search(query, type='track', limit=5)
    tracks = search_result['tracks']['items']
    if len(tracks) == 0:
        return None
    else:
        song_info_list = []
        for track_info in tracks:
            track_name = track_info['name']
            track_artist = track_info['artists'][0]['name']
            track_id = track_info['id']
            track_info = spotify.track(track_id)
            track_preview_url = track_info['preview_url']
            track_cover_url = track_info['album']['images'][0]['url']
            song_info = {'name': track_name, 'artist': track_artist, 'preview_url': track_preview_url, 'cover_url': track_cover_url}
            song_info_list.append(song_info)
        return song_info_list


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
