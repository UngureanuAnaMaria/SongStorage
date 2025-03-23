import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from SongStorage import SongStorage
from meth.open_add_song_window import open_add_song_window, button_style
from meth.open_delete_song_window import open_delete_song_window
from meth.open_create_save_list_window import open_create_save_list_window
from meth.open_play_song_window import open_play_song_window
from meth.open_modify_song_window import open_modify_song_window
from meth.open_search_songs_windo import open_search_songs_window

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