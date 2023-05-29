import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
from PIL import ImageTk, Image
import spotipy
import spotipy.util as util
import lyricsgenius

from spotify_credentials import CLIENT_ID, CLIENT_SECRET

# Ваши настройки
REDIRECT_URI = "http://localhost:8888/callback"  # Адрес перенаправления

# Права доступа, необходимые для работы с треком
SCOPE = "user-read-currently-playing"

# Аутентификация пользователя
username = "xqbzz"  # Замените на свой логин пользователя Spotify

token = util.prompt_for_user_token(
    username=username,
    scope=SCOPE,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
)

def get_track_lyrics(track_name, artists):
    genius = lyricsgenius.Genius("MRnCcT8B3I-doYHJ4TKJf-G5Tvz1xpV_xm66m9ZRMlXHjPXYlB4yj9bCMfq3CBBE")  # Замените "YOUR_GENIUS_API_TOKEN" на ваш собственный токен Genius API
    song = genius.search_song(track_name, artists)
    if song:
        return song.lyrics
    else:
        return "Текст песни не найден."

def update_track_info():
    if token:
        sp = spotipy.Spotify(auth=token)
        current_track = sp.current_user_playing_track()

        if current_track is None:
            track_name = "Сейчас ничего не играет."
            artists = ""
            image_url = ""  # Пустая ссылка на изображение
        else:
            track_name = current_track["item"]["name"]
            artists = ", ".join([artist["name"] for artist in current_track["item"]["artists"]])
            image_url = current_track["item"]["album"]["images"][0]["url"]  # URL изображения альбома
            lyrics = get_track_lyrics(track_name, artists)
    else:
        track_name = "Не удалось получить доступ к треку."
        artists = ""
        image_url = ""
        lyrics = ""

    # Обновление информации о треке в виджетах
    label_track.config(text="Сейчас играет: " + track_name)
    label_artists.config(text="Исполнитель(и): " + artists)

    # Загрузка и отображение изображения трека
    if image_url:
        response = requests.get(image_url)
        image_data = response.content
        with open("album_image.jpg", "wb") as f:
            f.write(image_data)
        image = Image.open("album_image.jpg")
        image = image.resize((150, 150), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        label_image.config(image=image)
        label_image.image = image

    # Обновление текста песни
    text_lyrics.config(state=tk.NORMAL)
    text_lyrics.delete(1.0, tk.END)
    text_lyrics.insert(tk.END, lyrics)
    text_lyrics.config(state=tk.DISABLED)

    # Планирование следующего обновления через 5 секунд
    window.after(5000, update_track_info)

def toggle_lyrics():
    if text_lyrics.winfo_viewable():
        text_lyrics.pack_forget()
        button_lyrics.config(text="Текст")
    else:
        text_lyrics.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        button_lyrics.config(text="Закрыть")

# Создание графического окна с помощью Tkinter
window = tk.Tk()
window.title("Текущий трек Spotify")
window.geometry("600x300")
window.configure(bg="#f0f0f0")  # Задание цвета фона окна

# Создание виджетов для отображения информации о треке
label_track = tk.Label(window, text="Сейчас играет:", font=("Arial", 14), bg="#f0f0f0")
label_artists = tk.Label(window, text="Исполнитель(и):", font=("Arial", 12), bg="#f0f0f0")
label_image = tk.Label(window, bg="#f0f0f0")
button_lyrics = tk.Button(window, text="Текст", font=("Arial", 12), command=toggle_lyrics)

# Создание виджета для отображения текста песни
text_lyrics = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
text_lyrics.config(state=tk.DISABLED)

# Размещение виджетов в окне
label_track.pack(pady=10, anchor=tk.W)
label_artists.pack(pady=5, anchor=tk.W)
label_image.pack(pady=10)
button_lyrics.pack(pady=5, anchor=tk.NE)
text_lyrics.pack_forget()

# Запуск первого обновления информации о треке
update_track_info()

# Запуск главного цикла событий Tkinter
window.mainloop()
