import shutil
import psycopg2
from pygame import mixer
import zipfile
import os

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