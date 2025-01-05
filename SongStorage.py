import os
import shutil
import psycopg2
from pygame import mixer
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import zipfile

class SongStorage:
    """
    A class for mapping songs in a storage system with metadata stored in a PostgreSQL database
    and the songs files in a storage folder.
    """

    def __init__(self):
        """
        Initialize the SongStorage class, setting up the storage directory and the
        database connection.
        """

        self.STORAGE_PATH = "Storage"
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
        """
        Adds a song file to the storage folder and its metadata to the database.

        Args:
            file_path (str): Song file path.
            metadata (tuple): A tuple containing artist, song_name, release_date and tags information.

        Returns:
            int: ID of the added song.

        Raises:
            ValueError: If not all metadata has been provided or the song already exists in database.
            FileExistsError: If the file already exists in the storage folder.
            Exception: If there are errors during copying the song file into storage folder or database operations.
        """

        if len(metadata) != 4:
            raise ValueError("Expected 4 metadata arguments: artist, song_name, release_date, and tags.")

        artist, song_name, release_date, tags = metadata

        if not os.path.exists(self.STORAGE_PATH):
            os.makedirs(self.STORAGE_PATH)

        file_name = os.path.basename(file_path)
        new_path = os.path.join(self.STORAGE_PATH, file_name)

        if os.path.exists(new_path):
            raise FileExistsError(f"File {file_name} already exists in storage folder.")

        self.db_cursor.execute(
            '''SELECT 1 FROM songs WHERE file_name = %s AND song_name = %s 
            AND artist = %s AND release_date = %s AND tags = %s LIMIT 1''',
            (file_name, artist, song_name, release_date, tags)
        )

        # Exista deja o melodie cu aceleasi date
        existing_song = self.db_cursor.fetchone()

        if existing_song:
            raise ValueError(f"A song with the same data already exists in the database.")

        try:
            shutil.copy(file_path, new_path)  # Copiaza fișierul in Storage
            print(f"File copied successfully to {new_path}.")
        except Exception as e:
            print(f"Error while adding the song {file_name} into storage folder: {e}.")
            raise

        try:
            self.db_cursor.execute(
                '''
                INSERT INTO songs (file_name, artist, song_name, release_date, tags)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
                ''',
                (file_name, artist, song_name, release_date, tags)
            )

            song_id = self.db_cursor.fetchone()[0]

            print(f"Song added successfully with ID: {song_id}.")
            return song_id
        except Exception as e:
            print(f"Error while adding the song {file_name} into database: {e}.")
            raise


    def delete_song(self, id_song):
        """
        Deletes a song file from storage file and its metadata from database.
        The song is identified by its ID.

        Args:
            id_song (int): ID of the song to delete.

        Raises:
            ValueError: If the song ID doesn't exist in the database.
            FileNotFoundError: If the song file doesn't exist in the storage folder.
            Exception: If there are errors during deleting the song file from storage folder or database operations.
        """

        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"No song found with ID: {id_song}")

        file_name = result[1]
        file_path = os.path.join(self.STORAGE_PATH, file_name)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"File {file_name} has been removed from storage folder.")
            except Exception as e:
                print(f"Error deleting the file from storage folder: {file_name}: {e}.")
                raise
        else:
            raise FileNotFoundError(f"File {file_name} does not exist in storage folder.")

        try:
            self.db_cursor.execute(
                '''DELETE FROM songs WHERE id = %s''',
                (id_song,)  # Tuplu
            )

            print(f"Song successfully deleted with ID: {id_song}.")
        except Exception as e:
            print(f"Error while deleting song with ID: {id_song} : {e}.")
            raise


    def modify_data(self, id_song, **metadata):
        """
        Modifies the metadata of a song existing in the database.
        The song is identified by its ID.

        Args:
            id_song (int): ID of the song to modify.
            **metadata: Key-value pairs representing the fields to update and their new values.

        Returns:
            None

        Raises:
             ValueError: If in the database isn't a song with the specified ID.
             Exception: If an error occurs during the database operation or during the modifying process.
        """

        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"No song found with ID: {id_song}")

        clauses = []
        values = []

        for clause, value in metadata.items():
            clauses.append(f"{clause} = %s")
            values.append(value)

        values.append(id_song)

        query = f"UPDATE songs SET {', '.join(clauses)} WHERE id = %s"
        try:
            self.db_cursor.execute(query, tuple(values))

            print(f"Song with ID: {id_song} succssfully modified.")
        except Exception as e:
            print(f"Error while modifying song with ID: {id_song} : {e}.")


    def search(self, **criteria):
        """
        Searches for songs in the database that meet the criteria.

        Args:
            **criteria: Key-value pairs representing the criteria for searching process.

        Returns:
            list: A list of matching songs.

        Raises:
            Exception: If there are errors in the database operation or in the search process.
        """

        try:
            clauses = []
            values = []

            for clause, value in criteria.items():
                if clause == "format":
                    clauses.append("file_name LIKE %s")
                    values.append(f"%.{value}")
                elif isinstance(value, list):  # Tags
                    clauses.append(f"{clause} && %s")  # PostgreSQL overlap array operator
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
        except Exception as e:
            print(f"Error while searching for songs: {e}")
            raise


    def create_save_list(self, arhive_path,**criteria):
        """
        Create a ZIP archive containing the song files that meet the given criteria.

        Args:
            arhive_path (str): Path to the archive.
            **criteria: Key-value pairs representing the criteria for searching songs process.

        Returns:
            list: A list of file names that has been added to the archive.

        Raises:
            Exception: If no songs match the criteria or an error occurs during the process.
        """

        try:
            songs = self.search(**criteria)

            if not songs:
                print("No songs match the criteria.")
                raise

            song_names = []

            with zipfile.ZipFile(arhive_path, 'w', zipfile.ZIP_DEFLATED) as arhive:
                for song in songs:
                    file_name = song[1]
                    file_path = os.path.join(self.STORAGE_PATH, file_name)

                    if os.path.exists(file_path):
                        print(f"Adding file: {file_path}.")
                        arhive.write(file_path, file_name)
                        print(f"Added {file_name} into arhive.")
                        song_names.append(file_name)
                    else:
                        print(f"File {file_path} not found.")

            return song_names
        except Exception as e:
            print(f"Error while creating the archive: {e}.")
            raise


    def play(self, file_path):
        """
        Plays a song file.

        Args:
            file_path (str): Path to the song file to play.
        """

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


    def pause(self):
        """
        Pauses the currently playing song.
        """

        mixer.music.pause()


    def resume(self):
        """
        Resumes a paused song.
        """

        mixer.music.unpause()


    def stop(self):
        """
        Stops the currently playing song.
        """

        mixer.music.stop()


    def get_all_songs(self):
        """
        Gets all songs stored into database.

        Returns:
            list: A list of song records from database.
        """

        self.db_cursor.execute("SELECT * FROM songs")
        return self.db_cursor.fetchall()


    def close_connection(self):
        """
        Closes the database connection and cursor.
        """

        self.db_cursor.close()
        self.db_conn.close()


button_style = {
        "bg": "#2B4C93", # Background colour
        "fg": "white", # Font colour
        "activebackground": "#3D65D5", # Background colour cand butonul e apasat
        "relief": "raised" # Stil margine
    }

song_label = None


def open_add_song_window(storage, tree):
    """
    Opens a window for adding a song, including its metadata and file.

    This function creates a GUI window where the user can input the artist, song_name, release_date, tags.
    The user can also browse for an audio file to join the song. After entering the information, the user can save the song
    and all the metadata will be displayed in the principal window(tree). Also, a success message is displayed in current window.

    Args:
        storage (SongStorage): An instance of SongStorage class used to add the song.
        tree (ttk.Treeview): The treeview widget representing main window.

    Returns:
        None

    Raises:
        ValueError: If any required fields (artist, song name, release date, tags or file) are missing.
        Exception: If there are errors adding the song to the storage folder or database or displaying it into the main window.
    """

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
        """
        Opens a file dialog for browsing and selecting an audio file.

        Updates the file path once is selected and display the file name in the current window.

        Args:
            None

        Returns:
            None
        """

        nonlocal file_path
        file_path = filedialog.askopenfilename(title="Select a Song File",
                                               filetypes=[("Audio Files",
                                                           "*.mp3;*.wav;*.flac;*.aac;*.ogg;*.m4a;*.wma;*.aiff;*.opus;"
                                                            "*.amr;*.alac;*.mka;*.dts;*.eac3;*.midi;*.mid;*.flv;*.ape;"
                                                            "*.vqf;*.tta;*.spx;*.raw;*.wv;*.snd;*.mpc;*.la;*.shn;*.aifc;"
                                                            "*.ac3;*.cda;*.dff;*.dsf;*.xm;*.mod;*.s3m;*.it;*.mtm;*.m4b;"
                                                            "*.pcaf;*.oga;*.aif;*.m3u;*.mpd;*.f4a;*.f4b;*.caf;*.w64")])
        if file_path:
            file_name = os.path.basename(file_path)
            file_label.config(text=f"Selected file: {file_name}")

    browse_button = tk.Button(add_song_window, text = "Browse File", command = browse_file, **button_style)
    browse_button.pack(pady = 10)

    file_label = tk.Label(add_song_window, text = "No file selected.")
    file_label.pack()

    def save_song():
        """
        Attempts to add a song into the database and storage folder.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If any required fields (artist, song name, release date, tags or file) are missing.
            Exception: If there are errors adding the song to the storage folder or database or displaying it into the main window.
        """

        global song_label
        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get().split(",")

        if not artist:
            print("No artist!")
            tk.messagebox.showerror("Error", "Please provide the artist.")
            raise ValueError("No artist!")

        if not song_name:
            print("No song name!")
            tk.messagebox.showerror("Error", "Please provide the song name.")
            raise ValueError("No song name!")

        if not release_date:
            print("No release date!")
            tk.messagebox.showerror("Error", "Please provide the release date.")
            raise ValueError("No release date!")

        if not tags:
            print("No tags!")
            tk.messagebox.showerror("Error", "Please provide the tags.")
            raise ValueError("No tags!")

        if not file_path:
            print("No file selected!")
            tk.messagebox.showerror("Error", "No file selected.")
            raise ValueError("No file path!")

        if song_label:
            song_label.config(text="")

        try:
            song_id = storage.add_song(file_path, artist, song_name, release_date, tags)
            print(f"Song added with ID: {song_id}.")

            song_id_label = tk.Label(add_song_window, text = f"Song added with ID: {song_id}.")
            song_id_label.pack()

            # Adaug in root window inregistrarea
            song = (song_id, file_path.split("/")[-1], artist, song_name, release_date, tags)
            tree.insert("", tk.END, values=song)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error adding song: {e}.")
            print(f"Error adding song: {e}.")
            raise

    save_button = tk.Button(add_song_window, text = "Save", command = save_song, **button_style)
    save_button.pack(pady = 15)

    add_song_window.mainloop()


def open_delete_song_window(storage, tree):
    """
    Open a window that allows the user to delete a song from storage folder and database.

    This function creates a GUI window where the user can input the song ID to delete. After the song is deleted,
    the entry corresponding the ID is also removed from main window and a success message is displayed in current window.

    Args:
        storage (SongStorage): An instance of SongStorage class used to delete the song.
        tree (ttk.Treeview): The treeview widget representing main window.

    Returns:
        None

    Raises:
        ValueError: If the song ID is missing.
        Exception: If there are errors in the deleting process or updating the main window.
    """

    delete_song_window = tk.Toplevel()
    delete_song_window.title("Delete Song")
    delete_song_window.geometry("600x600")

    tk.Label(delete_song_window, text="ID:").pack()
    id_entry = tk.Entry(delete_song_window)
    id_entry.pack(pady = 5)

    def delete_song():
        """
        Searches for a song based on the ID provided by the user and attempts to delete it from database and
        storage folder.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If the song ID is missing.
            Exception: If there are errors in the deleting process or updating the main window.
        """

        global song_label
        song_id = id_entry.get()

        if not song_id:
            print("No id!")
            tk.messagebox.showerror("Error", "Please provide the song id.")
            raise ValueError("No id!")

        if song_label:
            song_label.config(text="")

        try:
            storage.delete_song(song_id)
            print(f"Song deleted with ID: {song_id}.")

            song_label = tk.Label(delete_song_window, text = f"Song deleted with ID: {song_id}.")
            song_label.pack()

            # Elimin din root window inregistrarea
            for item in tree.get_children():
                tree_id = tree.item(item)["values"][0]

                if str(tree_id) == str(song_id):
                    tree.delete(item)
                    break
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error deleting song: {e}.")
            print(f"Error deleting song: {e}.")
            raise

    delete_buton = tk.Button(delete_song_window, text="Delete", command=delete_song, **button_style)
    delete_buton.pack(pady = 15)

    delete_song_window.mainloop()


def open_modify_song_window(storage, tree):
    """
    Open a window to modify the metadata of an existing song in the database.

    This function creates a GUI window that allows the user to provide the song ID and the new values for
    the metadata. After submitting the modification, the function attempts to update the song's information
    and if the modification is successful a message will be displayed in the window and the
    modifications will be displayed in the main window.

    Args:
        storage (SongStorage): An instance of SongStorage class used to modify the song.
        tree (ttk.Treeview): The treeview widget representing main window.

    Returns:
        None

    Raises:
        ValueError: If the song ID or no fields are provided for modification.
        Exception: Is there are errors during modifying the song information or updating the main window.
    """

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
        """
        Searches for a song based on the ID provided by the user and attempts to modify its metadata based on
        the info provided.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If the song ID or no fields are provided for modification.
            Exception: Is there are errors during modifying the song information or updating the main window.
        """

        global song_label
        song_id = id_entry.get()
        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get()

        if not song_id:
            print("No id!")
            tk.messagebox.showerror("Error", "Please provide the song id.")
            raise ValueError("No song id!")

        if not artist and not song_name and not release_date and not tags:
            print("No field to modify!")
            tk.messagebox.showerror("Error", "Please provide at least one field to modify.")
            raise ValueError("No field to modify!")

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

            if song_label:
                song_label.config(text = "")

            storage.modify_data(song_id, **updated_data)
            print(f"Song modified with ID: {song_id}.")

            song_label = tk.Label(modify_song_window, text = f"Song modified with ID: {song_id}.")
            song_label.pack()

            # Modific in root window inregistrarea
            for item in tree.get_children():
                tree_values = tree.item(item)["values"]

                if str(tree_values[0]) == str(song_id):
                    new_values = (
                        song_id,
                        tree_values[1],
                        artist if artist else tree_values[2],
                        song_name if song_name else tree_values[3],
                        release_date if release_date else tree_values[4],
                        " ".join(tags) if tags else tree_values[5],
                    )
                    tree.item(item, values = new_values)
                    break
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error modifying song: {e}.")
            print(f"Error modifying song: {e}.")

    modify_button = tk.Button(modify_song_window, text = "Modify", command = modify_song, **button_style)
    modify_button.pack(pady = 15)

    modify_song_window.mainloop()


def open_play_song_window(storage):
    """
    Opens a window for playing, pausing and stopping a song.

    This function creates a new GUI window with option for browsing and select an audio file,
    button for playing, pausing and stopping the selected song.

    Args:
        storage (SongStorage): An instance of SongStorage class used to control song playback.

    Returns:
        None

    Raises:
        ValueError: If no song file is selected before attempting to play a song.
        Exception: If there are errors during the playback process.
    """

    play_song_window = tk.Toplevel()
    play_song_window.title("Play Song")
    play_song_window.geometry("400x200")

    file_path = None
    is_playing = False
    is_paused = False

    def browse_file():
        """
        Opens a file dialog for browsing and selecting an audio file.

        Updates the file path once is selected and display the file name in the current window.

        Args:
            None

        Returns:
            None
        """

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

    file_label = tk.Label(play_song_window, text="No file selected.")
    file_label.pack(pady = 10)

    play_icon_path = os.path.join("icons", "play-button.png")
    pause_icon_path = os.path.join("icons", "pause-button.png")
    stop_icon_path = os.path.join("icons", "stop-button.png")

    def resize_icon(icon_path):
        """
        Resizes the provided icon to a standard size.

        Args:
            icon_path (str): The path to the icon image.

        Returns:
            ImageTk.PhotoImage: The resized icon image.
        """

        image = Image.open(icon_path)
        resize_image = image.resize((20, 20))
        return ImageTk.PhotoImage(resize_image)

    play_icon = resize_icon(play_icon_path)
    pause_icon = resize_icon(pause_icon_path)
    stop_icon = resize_icon(stop_icon_path)

    button_frame = tk.Frame(play_song_window)
    button_frame.pack(pady=10)

    def stop_song():
        """
        Stops the currently playing song and updates the buttons.

        Args:
            None

        Returns:
            None
        """

        nonlocal is_playing, is_paused

        storage.stop()
        play_button.config(image = stop_icon)
        is_playing = False
        is_paused = False
        play_button.config(image = play_icon)
        stop_button.pack_forget()

    stop_button = tk.Button(button_frame, image = stop_icon, command=stop_song)

    def play_song():
        """
        Play, pause and resume the song.

        If the song is not playing, it starts the playback, els it toggles between pause and resume.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If no song file is selected.
            Exception: If an error occurs during the process.
        """

        nonlocal is_playing, is_paused

        if not file_path:
            print("No file selected!")
            tk.messagebox.showerror("Error", "No file selected.")
            raise ValueError("No file selected!")

        try:
            if not is_playing:
                storage.play(file_path)
                is_playing = True
                play_button.config(image = pause_icon)
                stop_button.pack(side=tk.LEFT, padx = 5)
            elif is_paused:
                storage.resume()
                is_paused = False
                play_button.config(image = pause_icon)
            else:
                storage.pause()
                is_paused = True
                play_button.config(image = play_icon)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error playing song: {e}.")
            print(f"Error playing song: {e}.")
            raise

    play_button = tk.Button(button_frame, image = play_icon, command=play_song)
    play_button.pack(side=tk.LEFT, padx = 5)

    def on_close():
        """
        Stops the song playback when the window is closed.

        Args:
            None

        Returns:
            None
        """

        storage.stop()
        play_song_window.destroy()

    play_song_window.protocol("WM_DELETE_WINDOW", on_close)

    play_song_window.mainloop()


def open_search_songs_window(storage):
    """
    Opens a window for searching song based on various criteria.

    This function opens a GUI window where the user can input the criteria for searching, such as artist, song name, release date,
    tags, format. After submitting the results will appear in a table in the current window. If no input is provided all datas from
    database will represent the result.

     Args:
        storage (SongStorage): An instance of SongStorage class used to search songs.

    Returns:
         None

    Raises:
        Exception: If there are errors during the search process.
    """

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
        """
        Searches for songs based on the user input and display the results.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: If there are errors during the search process.
        """

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
            print(f"Search results: {results}.")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error searching songs: {e}.")
            print(f"Error searching songs: {e}.")
            raise

    search_button = tk.Button(search_songs_window, text = "Search", command = search_songs, **button_style)
    search_button.pack(pady = 15)

    search_songs_window.mainloop()


def open_create_save_list_window(storage):
    """
    Opens a window for creating a song archive based on various criteria.

    This function opens a GUI window where the user can input the criteria for searching songs to add in the archive,
    such as artist, song name, release date, tags, format. It also allows the user to browse and select an archive file.
    After submitting, the song are added in the archive and a message is displayed in the current window.

     Args:
        storage (SongStorage): An instance of SongStorage class used for creating the save list and handling the archive.

    Returns:
         None

    Raises:
        ValueError: If no archive file is selected or no songs are added to the archive.
        Exception: If there are errors during the create save list process.
    """

    create_save_list_window = tk.Toplevel()
    create_save_list_window.title("Create Save List")
    create_save_list_window.geometry("600x600")

    tk.Label(create_save_list_window, text="Artist:").pack()
    artist_entry = tk.Entry(create_save_list_window)
    artist_entry.pack(pady = 5)

    tk.Label(create_save_list_window, text="Song Name:").pack()
    song_name_entry = tk.Entry(create_save_list_window)
    song_name_entry.pack(pady = 5)

    tk.Label(create_save_list_window, text="Release Date (YYYY-MM-DD):").pack()
    release_date_entry = tk.Entry(create_save_list_window)
    release_date_entry.pack(pady = 5)

    tk.Label(create_save_list_window, text="Tags (comma separated):").pack()
    tags_entry = tk.Entry(create_save_list_window)
    tags_entry.pack(pady = 5)

    tk.Label(create_save_list_window, text="Format:").pack()
    format_entry = tk.Entry(create_save_list_window)
    format_entry.pack(pady=5)

    arhive_path = None

    def browse_file():
        """
        Opens a file dialog for browsing and selecting an archive file.

        Updates the file path once is selected and display the file name in the current window.

        Args:
            None

        Returns:
            None
        """

        nonlocal arhive_path
        arhive_path = filedialog.askopenfilename(title="Select a Arhive File",
                                                 filetypes=[
                                                     ("ZIP Archive", "*.zip"),
                                                     ("TAR Archive", "*.tar"),
                                                     ("Gzipped TAR Archive", "*.tar.gz"),
                                                     ("RAR Archive", "*.rar"),
                                                     ("7z Archive", "*.7z"),
                                                     ("Bzip2 Archive", "*.bz2"),
                                                     ("XZ Archive", "*.xz"),
                                                     ("CAB Archive", "*.cab"),
                                                     ("ARJ Archive", "*.arj"),
                                                     ("LZH Archive", "*.lzh"),
                                                     ("Z Archive", "*.z"),
                                                     ("ISO Image", "*.iso"),
                                                     ("DMG Image", "*.dmg"),
                                                     ("LZMA TAR Archive", "*.tar.lzma"),
                                                     ("CPIO Archive", "*.cpio"),
                                                     ("All Archive Files",
                                                      "*.zip;*.tar;*.tar.gz;*.tar.bz2;*.tar.xz;*.rar;*.7z;*.bz2;*.xz;*.cab;*.arj;*.lzh;*.z;*.iso;*.dmg;*.tar.lzma;*.cpio")
                                                 ])
        if arhive_path:
            file_name = os.path.basename(arhive_path)
            file_label.config(text=f"Selected file: {file_name}")

    browse_button = tk.Button(create_save_list_window, text="Browse File", command=browse_file, **button_style)
    browse_button.pack(pady=5)

    file_label = tk.Label(create_save_list_window, text="No file selected.")
    file_label.pack(pady=10)

    def create_save_list():
        """
        Creates a save list from the user input data and adds them to the selected archive.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: If no archive file is selected or no songs are added to the archive.
            Exception: If there are errors during the create save list process.
        """

        artist = artist_entry.get()
        song_name = song_name_entry.get()
        release_date = release_date_entry.get()
        tags = tags_entry.get()
        format = format_entry.get()

        if not arhive_path:
            print("No file selected!")
            tk.messagebox.showerror("Error", "No file selected.")
            raise ValueError("No file selected!")

        try:
            global song_label
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

            songs = storage.create_save_list(arhive_path, **data)

            if song_label:
                song_label.config(text = "")

            if songs:
                song_names = "\n".join(songs)
                print(f"Songs added info arhive: {song_names}.")

                song_label = tk.Label(create_save_list_window, text = "")
                song_label.config(text = f"Songs added info arhive:\n" + song_names)
                song_label.pack()
            else:
                print("No songs were added.")

                song_label = tk.Label(create_save_list_window, text = "No songs were added.")
                song_label.pack()

                raise ValueError("No songs were added.")

        except Exception as e:
            tk.messagebox.showerror("Error", f"Error during creating arhive: {e}.")
            print(f"Error during creating arhive: {e}.")

    create_save_list_button = tk.Button(create_save_list_window, text = "Create Save List", command = create_save_list, **button_style)
    create_save_list_button.pack(pady = 15)

    create_save_list_window.mainloop()


def main():
    """
    This function initialize the SongStorage system, creates the main application window using Tkinter where all
    the data from database will be displayed in a table and set up the buttons for various operations (add, delete,
    modify, search, play, create save list).

    Args:
        None

    Returns:
        None
    """

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

    search_button = tk.Button(button_frame, text="Search Songs", command=lambda: open_search_songs_window(storage), **button_style)
    search_button.pack(side=tk.LEFT, padx=20)

    create_save_list_button = tk.Button(button_frame, text="Create Save List",command=lambda: open_create_save_list_window(storage),
                              **button_style)
    create_save_list_button.pack(side=tk.LEFT, padx=20)

    play_button = tk.Button(button_frame, text="Play Song", command=lambda: open_play_song_window(storage), **button_style)
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