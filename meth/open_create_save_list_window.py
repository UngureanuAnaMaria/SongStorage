import tkinter as tk
from tkinter import filedialog
import os

button_style = {
        "bg": "#2B4C93", # Background colour
        "fg": "white", # Font colour
        "activebackground": "#3D65D5", # Background colour cand butonul e apasat
        "relief": "raised" # Stil margine
    }

song_label = None


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
