import os
import shutil

class SongStorage:
    def __init__(self):
        self.STORAGE_PATH = "C:/Users/anaun/OneDrive/Desktop/Storage"

    def add_song_to_dir(self, file_path):
        if not os.path.exists(self.STORAGE_PATH):
            os.makedirs(self.STORAGE_PATH)

        file_name = os.path.basename(file_path)
        new_path = os.path.join(self.STORAGE_PATH, file_name)

        shutil.copy(file_path, new_path)  # Copiaza fișierul in Storage
        return new_path


print(SongStorage().add_song_to_dir("C:/Users/anaun/Downloads/sample-file-1.wav"))
