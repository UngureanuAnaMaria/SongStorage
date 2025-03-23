import tkinter as tk
from tkinter import ttk

button_style = {
        "bg": "#2B4C93", # Background colour
        "fg": "white", # Font colour
        "activebackground": "#3D65D5", # Background colour cand butonul e apasat
        "relief": "raised" # Stil margine
    }

song_label = None


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