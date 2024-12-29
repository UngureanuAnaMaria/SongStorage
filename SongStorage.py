import os
import shutil
import psycopg2
from pygame import mixer
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk


class SongStorage:
    def __init__(self):
        self.STORAGE_PATH = "C:/Users/anaun/OneDrive/Desktop/Storage"
        self.db_conn = psycopg2.connect(
            database="SongStorage",
            user='postgres',
            password='password',
            host='localhost',
            port='5432'
        )
        self.db_conn.autocommit = True
        self.db_cursor = self.db_conn.cursor()

    def add_song(self, file_path, *metadata):
        #exception song_name unique(maybe update database)
        #excep  o inregistrare cu aceleasi date(sa nu existe duplicate)
        #excep song already in Storage folder
        if len(metadata) != 4:
            raise ValueError("Expected 4 metadata arguments: artist, song_name, release_date, and tags")

        artist, song_name, release_date, tags = metadata

        if not os.path.exists(self.STORAGE_PATH):
            os.makedirs(self.STORAGE_PATH)

        file_name = os.path.basename(file_path)
        new_path = os.path.join(self.STORAGE_PATH, file_name)

        shutil.copy(file_path, new_path)  # Copiaza fișierul in Storage
        self.db_cursor.execute(
            '''
            INSERT INTO songs (file_name, artist, song_name, release_date, tags)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            ''',
            (file_name, artist, song_name, release_date, tags)
        )
        song_id = self.db_cursor.fetchone()[0]

        return song_id

    def delete_song(self, id_song):
        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"no song found with id : {id_song}")

        self.db_cursor.execute(
            '''DELETE FROM songs WHERE id = %s''',
            (id_song,) # Tuplu
        )

    def modify_data(self, id_song, **metadata):
        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"No song found with id : {id_song}")

        clauses = []
        values = []

        for clause, value in metadata.items():
            clauses.append(f"{clause} = %s")
            values.append(value)

        values.append(id_song)

        query = f"UPDATE songs SET {', '.join(clauses)} WHERE id = %s"
        self.db_cursor.execute(query, tuple(values))

    def search(self, **criteria):
        clauses = []
        values = []

        for clause, value in criteria.items():
            if clause == "format":
                clauses.append("file_name LIKE %s")
                values.append(f"%.{value}")
            elif isinstance(value, list):  # Tags
                clauses.append(f"{clause} && %s")  # PostgreSQL overlap array operator????
                values.append(value)
            else:
                clauses.append(f"{clause} = %s")
                values.append(value)

        where_clause = 'AND '.join(clauses)

        query = "SELECT * FROM songs"
        if clauses:
            query += f" WHERE {where_clause}"

        self.db_cursor.execute(query, tuple(values))

        results = self.db_cursor.fetchall()

        if not results:
            print("No songs match the criteria.")
            return []

        return results

    def play(self, file_path):
        mixer.init()
        mixer.music.load(file_path)
        mixer.music.set_volume(0.7)
        mixer.music.play()

        # Play in consola
        # while True:
        #
        #     print("Press 'p' to pause, 'r' to resume")
        #     print("Press 'e' to exit the program")
        #     query = input("  ")
        #
        #     if query == 'p':
        #         mixer.music.pause()
        #     elif query == 'r':
        #         mixer.music.unpause()
        #     elif query == 'e':
        #         mixer.music.stop()
        #         break

    def pause(self, file_path):
        mixer.music.pause()

    def resume(self, file_path):
        mixer.music.unpause()

    def stop(self, file_path):
        mixer.music.stop()

    def get_all_songs(self):
        self.db_cursor.execute("SELECT * FROM songs")
        return self.db_cursor.fetchall()

    def close_connection(self):
        self.db_cursor.close()
        self.db_conn.close()

#SongStorage().delete_song(6)
#SongStorage().modify_data(1, song_name="New Song fcercName")
#SongStorage().close_connection()

#Loguri rulare program?????????????????????????????????????????????????????????????????????

button_style = {
        "bg": "#2B4C93", # Background colour
        "fg": "white", # Font colour
        "activebackground": "#3D65D5", # Background colour cand butonul e apasat
        "relief": "raised" # Stil margine
    }

def open_add_song_window(storage, tree):
    add_song_window = tk.Toplevel()
    add_song_window.title("Add Song")
    add_song_window.geometry("600x600")

    tk.Label(add_song_window, text="Artist:").pack()
    artist_entry = tk.Entry(add_song_window)
    artist_entry.pack(pady = 5)

    tk.Label(add_song_window, text="Song Name:").pack()
    song_name_entry = tk.Entry(add_song_window)
    song_name_entry.pack(pady = 5)

    tk.Label(add_song_window, text="Release Date (YYYY-MM-DD):").pack()
    release_date_entry = tk.Entry(add_song_window)
    release_date_entry.pack(pady = 5)

    tk.Label(add_song_window, text="Tags (comma separated):").pack()
    tags_entry = tk.Entry(add_song_window)
    tags_entry.pack(pady = 5)

    file_path = None


    def browse_file():
        nonlocal file_path
        file_path = filedialog.askopenfilename(title="Select a Song File",
                                               filetypes=[("Audio Files", "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a;*.wma;*.aiff;*.opus;*.amr;*.alac;*.mka;*.dts;"
                                                                          "*.eac3;*.midi;*.mid;*.flv;*.ape;*.vqf;*.tta;*.spx;*.raw;*.wv;*.snd;*.mpc;*.la;*.shn;"
                                                                          "*.aifc;*.ac3;*.cda;*.dff;*.dsf;*.xm;*.mod;*.s3m;*.it;*.mtm;*.m4b;*.pcaf;*.oga;*.aif;"
                                                                          "*.m3u;*.mpd;*.f4a;*.f4b;*.caf;*.w64")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_label.config(text=f"Selected file: {file_name}")

    browse_button = tk.Button(add_song_window, text = "Browse File", command = browse_file, **button_style)
    browse_button.pack(pady = 10)

    file_label = tk.Label(add_song_window, text = "No file selected")
    file_label.pack()


    def save_song():
        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get().split(",")

        if not artist:
            print("No artist!")
            tk.messagebox.showerror("Error", "Please provide the artist")
            return

        if not song_name:
            print("No song name!")
            tk.messagebox.showerror("Error", "Please provide the song name")
            return

        if not release_date:
            print("No release date!")
            tk.messagebox.showerror("Error", "Please provide the release date")
            return

        if not tags:
            print("No tags!")
            tk.messagebox.showerror("Error", "Please provide the tags")
            return

        if not file_path:
            print("No file selected!")
            tk.messagebox.showerror("Error", "No file selected")
            return

        try:
            song_id = storage.add_song(file_path, artist, song_name, release_date, tags)
            print(f"Song added with ID: {song_id}")

            song_id_label = tk.Label(add_song_window, text="")
            song_id_label.config(text=f"Song added with ID: {song_id}")
            song_id_label.pack()

            # Adaug in root window inregistrarea
            song = (song_id, file_path.split("/")[-1], artist, song_name, release_date, tags)
            tree.insert("", tk.END, values=song)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error adding song: {e}")
            print(f"Error adding song: {e}")

    save_button = tk.Button(add_song_window, text = "Save", command = save_song, **button_style)
    save_button.pack(pady = 15)

    add_song_window.mainloop()


def open_delete_song_window(storage, tree):
    delete_song_window = tk.Toplevel()
    delete_song_window.title("Delete Song")
    delete_song_window.geometry("600x600")

    tk.Label(delete_song_window, text="ID:").pack()
    id_entry = tk.Entry(delete_song_window)
    id_entry.pack(pady = 5)

    def delete_song():
        song_id = id_entry.get()

        if not song_id:
            print("No id!")
            tk.messagebox.showerror("Error", "Please provide the song id")
            return

        try:
            storage.delete_song(song_id)
            print(f"Song deleted with ID: {song_id}")

            song_label = tk.Label(delete_song_window, text="")
            song_label.config(text=f"Song deleted with ID: {song_id}")
            song_label.pack()

            # Elimin din root window inregistrarea
            for item in tree.get_children():
                tree_id = tree.item(item)["values"][0]

                if str(tree_id) == str(song_id):
                    tree.delete(item)
                    break
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error deleting song: {e}")
            print(f"Error deleting song: {e}")

    delete_buton = tk.Button(delete_song_window, text="Delete", command=delete_song, **button_style)
    delete_buton.pack(pady = 15)

    delete_song_window.mainloop()


def open_modify_song_window(storage, tree):
    modify_song_window = tk.Toplevel()
    modify_song_window.title("Modify Song")
    modify_song_window.geometry("600x600")

    tk.Label(modify_song_window, text="ID:").pack()
    id_entry = tk.Entry(modify_song_window)
    id_entry.pack(pady = 5)

    tk.Label(modify_song_window, text="Artist:").pack()
    artist_entry = tk.Entry(modify_song_window)
    artist_entry.pack(pady = 5)

    tk.Label(modify_song_window, text="Song Name:").pack()
    song_name_entry = tk.Entry(modify_song_window)
    song_name_entry.pack(pady = 5)

    tk.Label(modify_song_window, text="Release Date (YYYY-MM-DD):").pack()
    release_date_entry = tk.Entry(modify_song_window)
    release_date_entry.pack(pady = 5)

    tk.Label(modify_song_window, text="Tags (comma separated):").pack()
    tags_entry = tk.Entry(modify_song_window)
    tags_entry.pack(pady = 5)

    def modify_song():
        song_id = id_entry.get()
        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get()

        if not song_id:
            print("No id!")
            tk.messagebox.showerror("Error", "Please provide the song id")
            return

        if not artist and not song_name and not release_date and not tags:
            print("No field to modify!")
            tk.messagebox.showerror("Error", "Please provide at least one field to modify")
            return

        try:
            updated_data = {}

            if artist:
                updated_data["artist"] = artist

            if song_name:
                updated_data["song_name"] = song_name

            if release_date:
                updated_data["release_date"] = release_date

            if tags:
                tags = tags.split(",")
                updated_data["tags"] = tags

            storage.modify_data(song_id, **updated_data)
            print(f"Song modified with ID: {song_id}")

            song_label = tk.Label(modify_song_window, text="")
            song_label.config(text=f"Song modified with ID: {song_id}")
            song_label.pack()

            # Modific in root window inregistrarea
            # song = (song_id, file_path.split("/")[-1], artist, song_name, release_date, tags)
            # tree.insert("", tk.END, values=song)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error modifying song: {e}")
            print(f"Error modifying song: {e}")

    modify_button = tk.Button(modify_song_window, text = "Modify", command = modify_song, **button_style)
    modify_button.pack(pady = 15)

    modify_song_window.mainloop()


def open_play_song_window(storage, tree):
    play_song_window = tk.Toplevel()
    play_song_window.title("Play Song")
    play_song_window.geometry("300x100")

    file_path = None
    is_playing = False
    is_paused = False

    def browse_file():
        nonlocal file_path
        file_path = filedialog.askopenfilename(title="Select a Song File",
                                               filetypes=[("Audio Files",
                                                           "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a;*.wma;*.aiff;*.opus;*.amr;*.alac;*.mka;*.dts;"
                                                           "*.eac3;*.midi;*.mid;*.flv;*.ape;*.vqf;*.tta;*.spx;*.raw;*.wv;*.snd;*.mpc;*.la;*.shn;"
                                                           "*.aifc;*.ac3;*.cda;*.dff;*.dsf;*.xm;*.mod;*.s3m;*.it;*.mtm;*.m4b;*.pcaf;*.oga;*.aif;"
                                                           "*.m3u;*.mpd;*.f4a;*.f4b;*.caf;*.w64")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_label.config(text=f"Selected file: {file_name}")

    browse_button = tk.Button(play_song_window, text="Browse File", command=browse_file, **button_style)
    browse_button.pack(pady = 5)

    file_label = tk.Label(play_song_window, text="No file selected")
    file_label.pack(pady = 10)

    play_icon_path = os.path.join("icons", "play-button.png")
    pause_icon_path = os.path.join("icons", "pause-button.png")
    stop_icon_path = os.path.join("icons", "stop-button.png")

    def resize_icon(icon_path):
        image = Image.open(icon_path)
        resize_image = image.resize((20, 20))
        return ImageTk.PhotoImage(resize_image)

    play_icon = resize_icon(play_icon_path)
    pause_icon = resize_icon(pause_icon_path)
    stop_icon = resize_icon(stop_icon_path)

    button_frame = tk.Frame(play_song_window)
    button_frame.pack(pady=10)

    def stop_song():
        nonlocal is_playing, is_paused
        storage.stop(file_path)
        play_button.config(image = stop_icon)
        is_playing = False
        is_paused = False
        play_button.config(image = play_icon)
        stop_button.pack_forget()

    stop_button = tk.Button(button_frame, image = stop_icon, command=stop_song)

    def play_song():
        nonlocal is_playing, is_paused

        if not file_path:
            print("No file selected!")
            tk.messagebox.showerror("Error", "No file selected")
            return

        try:
            if not is_playing:
                storage.play(file_path)
                is_playing = True
                play_button.config(image = pause_icon)
                stop_button.pack(side=tk.LEFT, padx = 5)
            elif is_paused:
                storage.resume(file_path)
                is_paused = False
                play_button.config(image = pause_icon)
            else:
                storage.pause(file_path)
                is_paused = True
                play_button.config(image = play_icon)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error playing song: {e}")
            print(f"Error playing song: {e}")

    play_button = tk.Button(button_frame, image = play_icon, command=play_song)
    play_button.pack(side=tk.LEFT, padx = 5)

    def on_close():
        storage.stop(file_path)
        play_song_window.destroy()

    play_song_window.protocol("WM_DELETE_WINDOW", on_close)

    play_song_window.mainloop()


def open_search_songs_window(storage, tree):
    search_songs_window = tk.Toplevel()
    search_songs_window.title("Search Songs")
    search_songs_window.geometry("1200x600")

    tk.Label(search_songs_window, text="Artist:").pack()
    artist_entry = tk.Entry(search_songs_window)
    artist_entry.pack(pady = 5)

    tk.Label(search_songs_window, text="Song Name:").pack()
    song_name_entry = tk.Entry(search_songs_window)
    song_name_entry.pack(pady = 5)

    tk.Label(search_songs_window, text="Release Date (YYYY-MM-DD):").pack()
    release_date_entry = tk.Entry(search_songs_window)
    release_date_entry.pack(pady = 5)

    tk.Label(search_songs_window, text="Tags (comma separated):").pack()
    tags_entry = tk.Entry(search_songs_window)
    tags_entry.pack(pady = 5)

    tk.Label(search_songs_window, text="Format:").pack()
    format_entry = tk.Entry(search_songs_window)
    format_entry.pack(pady=5)

    tree_search = None
    def search_songs():
        nonlocal tree_search

        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get()
        format = format_entry.get()

        try:
            data = {}

            if artist:
                data["artist"] = artist

            if song_name:
                data["song_name"] = song_name

            if release_date:
                data["release_date"] = release_date

            if tags:
                tags = tags.split(",")
                data["tags"] = tags

            if format:
                data["format"] = format

            results = storage.search(**data)

            if tree_search:
                tree_search.destroy()

            columns = ("id", "file_name", "artist", "song_name", "release_date", "tags")
            tree_search = ttk.Treeview(search_songs_window, columns=columns, show='headings')

            tree_search.heading("id", text="ID")
            tree_search.heading("file_name", text="File Name")
            tree_search.heading("artist", text="Artist")
            tree_search.heading("song_name", text="Song Name")
            tree_search.heading("release_date", text="Release Date")
            tree_search.heading("tags", text="Tags")

            tree_search.column("id", width=20)
            tree_search.column("release_date", width=50)

            for song in results:
                tree_search.insert("", tk.END, values=song)

            tree_search.pack(fill=tk.BOTH, expand=True)
            print(f"Results: {results}")

            # song_label = tk.Label(search_songs_window, text="")
            # song_label.config(text=f"Results: {results}")
            # song_label.pack()
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error searching songs: {e}")
            print(f"Error searching songs: {e}")

    search_button = tk.Button(search_songs_window, text = "Search", command = search_songs, **button_style)
    search_button.pack(pady = 15)

    search_songs_window.mainloop()


def main():
    storage = SongStorage()

    root = tk.Tk()
    root.title("Song Storage")
    root.geometry("1200x600")

    button_frame = tk.Frame(root)
    button_frame.pack(pady = 20) # Adauga un spatiu vertical intre frame si restul ferestrei

    save_button = tk.Button(button_frame, text="Add Song", command = lambda: open_add_song_window(storage, tree), **button_style)
    save_button.pack(side = tk.LEFT, padx = 20) # Spatiu intre butoane

    delete_button = tk.Button(button_frame, text="Delete Song", command=lambda: open_delete_song_window(storage, tree), **button_style)
    delete_button.pack(side = tk.LEFT, padx = 20)

    modify_button = tk.Button(button_frame, text="Modify Song", command=lambda: open_modify_song_window(storage, tree), **button_style)
    modify_button.pack(side = tk.LEFT, padx = 20)

    search_button = tk.Button(button_frame, text="Search Songs", command=lambda: open_search_songs_window(storage, tree), **button_style)
    search_button.pack(side=tk.LEFT, padx=20)

    play_button = tk.Button(button_frame, text="Play Song", command=lambda: open_play_song_window(storage, tree), **button_style)
    play_button.pack(side = tk.LEFT, padx = 20)

    columns = ("id", "file_name", "artist", "song_name", "release_date", "tags")
    tree = ttk.Treeview(root, columns=columns, show='headings')

    tree.heading("id", text = "ID")
    tree.heading("file_name", text = "File Name")
    tree.heading("artist", text = "Artist")
    tree.heading("song_name", text = "Song Name")
    tree.heading("release_date", text = "Release Date")
    tree.heading("tags", text = "Tags")

    tree.column("id", width = 20)
    tree.column("release_date", width = 50)

    songs = storage.get_all_songs()
    for song in songs:
        tree.insert("", tk.END, values = song)

    tree.pack(fill = tk.BOTH, expand = True)
    root.mainloop()

if __name__ == "__main__":
    main()

