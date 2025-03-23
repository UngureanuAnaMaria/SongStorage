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
