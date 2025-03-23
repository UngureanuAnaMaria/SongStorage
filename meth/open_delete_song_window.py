import tkinter as tk
from tkinter import ttk

button_style = {
        "bg": "#2B4C93", # Background colour
        "fg": "white", # Font colour
        "activebackground": "#3D65D5", # Background colour cand butonul e apasat
        "relief": "raised" # Stil margine
    }

song_label = None


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

