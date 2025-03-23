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
