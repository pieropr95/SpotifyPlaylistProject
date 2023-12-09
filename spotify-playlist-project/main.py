import os
import pandas as pd
from tkinter import *

from data.spotify_api import SpotifyAPI

BASE_DIR = os.path.dirname(__file__)
EXPORT_PATH = os.path.join(BASE_DIR, 'export')

client_id = '...'
client_secret = '...'


def main():
    print_header()
    input_loop()


def input_loop():
    while True:
        val = input('Exportar Playlist (y/n): ').lower().strip()
        if val == 'y':
            do_export()
        elif val == 'n':
            print('Bye')
            break
        else:
            print(f'Caso indefinido: {val}')
        print()
        print()


def do_export():
    spotify = SpotifyAPI(client_id, client_secret)

    # spotify.get_artist('1hCkSJcXREhrodeIHQdav8')
    # spotify.get_album('41zMFsCjcGenYKVJYUXU2n')

    playlists_list = spotify.get_my_playlists()
    user_playlists = playlists_list['items']
    array = []
    for x, list in enumerate(user_playlists):
        list_name = list['name']
        list_total = list['tracks']['total']
        list_id = list['id']
        array.append([list_name, list_total, list_id])
    
    playlists_list = spotify.get_my_playlists(offset=50)
    user_playlists = playlists_list['items']
    for x, list in enumerate(user_playlists):
        list_name = list['name']
        list_total = list['tracks']['total']
        list_id = list['id']
        array.append([list_name, list_total, list_id])

    df = pd.DataFrame(array, columns=['Name', 'Tracks', 'ID'])
    print(df.head(100))
    create_gui(df)

    val = input('Escoger Playlist: ').lower().strip()
    try:
        list_index = int(val)
    except:
        print(f'Valor {val} debe ser un entero')
        return
    
    list_id = df.iloc[list_index]['ID']
    print(list_id)

    playlist = spotify.get_playlist(list_id)

    # playlist = spotify.get_playlist('4uMnDvSST3EK2rl7oXVolp') # Road Tunes VOL. 1
    # playlist = spotify.get_playlist('7GpqyzGkilUllBeXfOVJti') # High Energy

    playlist_name = playlist['name']
    print(f'List: {playlist_name}')

    playlist_songs = playlist['tracks']['items']

    first_song_name = playlist_songs[0]['track']['name']
    first_song_artist = playlist_songs[0]['track']['artists'][0]['name']
    first_song_album = playlist_songs[0]['track']['album']['name']
    first_song_date = playlist_songs[0]['track']['album']['release_date']
    print(f'Name > {first_song_name}')
    print(f'Artist > {first_song_artist}')
    print(f'Album > {first_song_album}')
    print(f'Release Date > {first_song_date}')

    data = []
    for i, song in enumerate(playlist_songs):
        song_name = song['track']['name']
        artists = []
        for a, artist in enumerate(song['track']['artists']):
            artists.append(artist['name'])
        song_artist = ', '.join(artists)
        song_album = song['track']['album']['name']
        song_release_date = song['track']['album']['release_date']
        song_id = song['track']['id']
        data.append([i+1, song_name, song_artist, song_album, song_release_date, song_id])

    df_playlist = pd.DataFrame(data, columns=['N', 'Title', 'Artist', 'Album', 'Release Date', 'ID'])
    df_playlist.set_index('N', inplace=True)
    print(df_playlist.head(30))

    # EXCEL
    filename = playlist_name + '.xlsx'
    filepath = os.path.join(EXPORT_PATH, filename)
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    df_playlist.to_excel(writer, sheet_name='Playlist')

    worksheet = writer.sheets['Playlist']
    worksheet.set_column('B:F', 30)

    writer.save()


def create_gui(df):
    app = Tk()

    # PLAYLIST
    playlist_text = StringVar()
    playlist_label = Label(app, text='Playlist Name', font=('bold', 9), pady=20)
    playlist_label.grid(row=0, column=0, sticky=W)
    playlist_entry = Entry(app, textvariable=playlist_text)
    playlist_entry.grid(row=0, column=1)

    # USER
    user_text = StringVar()
    user_label = Label(app, text='User Name', font=('bold', 9))
    user_label.grid(row=0, column=2, sticky=W)
    user_entry = Entry(app, textvariable=user_text)
    user_entry.grid(row=0, column=3)

    # PLAYLISTS LIST
    playlists_listbox = Listbox(app, height=8, width=50)
    playlists_listbox.grid(row=2, column=0, columnspan=3, rowspan=6, pady=20, padx=20)
    for i in df.index:
        playlists_listbox.insert(END, (df['Name'][i], df['Tracks'][i]))

    # CREATE SCROLLBAR
    scrollbar = Scrollbar(app)
    scrollbar.grid(row=2, column=3)

    # SET SCROLLBAR TO LISTBOX
    playlists_listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=playlists_listbox.yview)

    # BUTTONS
    select_btn = Button(app, text='Select Playlist', width=12, command=select_item)
    select_btn.grid(row=1, column=0, pady=20)

    # BIND HIGHLIGHT EVENT
    playlists_listbox.bind('<<ListboxSelect>>', highlight_item)

    app.title('Spotify Manager')
    app.geometry('700x350')
    app.mainloop()


def select_item():
    print('SELECT ITEM')


def highlight_item(event):
    print('HIGHLIGHT ITEM')


def print_header():
    print("*** PROGRAMA DE EXPORTACIÓN DE PLAYLISTS EN SPOTIFY ***")
    print()

if __name__ == '__main__':
    main()
