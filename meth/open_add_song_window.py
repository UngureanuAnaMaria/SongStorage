import tkinter as tk
from tkinter import ttk, filedialog
import os

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