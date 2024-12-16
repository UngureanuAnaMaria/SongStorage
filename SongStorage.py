import os
import shutil
import datetime

import psycopg2

class SongStorage:
    def __init__(self):
        self.STORAGE_PATH = "C:/Users/anaun/OneDrive/Desktop/Storage"
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
        #exception song_name unique(maybe update database)
        #excep  o inregistrare cu aceleasi date(sa nu existe duplicate)
        #excep song already in Storage folder
        if len(metadata) != 4:
            raise ValueError("Expected 4 metadata arguments: artist, song_name, release_date, and tags")

        artist, song_name, release_date, tags = metadata

        if not os.path.exists(self.STORAGE_PATH):
            os.makedirs(self.STORAGE_PATH)

        file_name = os.path.basename(file_path)
        new_path = os.path.join(self.STORAGE_PATH, file_name)

        shutil.copy(file_path, new_path)  # Copiaza fișierul in Storage
        self.db_cursor.execute(
            '''
            INSERT INTO songs (file_name, artist, song_name, release_date, tags)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            ''',
            (file_name, artist, song_name, release_date, tags)
        )
        song_id = self.db_cursor.fetchone()[0]

        return song_id

    def delete_song(self, id_song):
        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"no song found with id : {id_song}")

        self.db_cursor.execute(
            '''DELETE FROM songs WHERE id = %s''',
            (id_song,) # Tuplu
        )

    def modify_data(self, id_song, **metadata):
        self.db_cursor.execute(
            '''SELECT * FROM songs WHERE id = %s''',
            (id_song,)
        )

        result = self.db_cursor.fetchone()

        if not result:
            raise ValueError(f"no song found with id : {id_song}")

        clauses = []
        values = []

        for clause, value in metadata.items():
            clauses.append(f"{clause} = %s")
            values.append(value)

        values.append(id_song)

        query = f"UPDATE songs SET {', '.join(clauses)} WHERE id = %s"
        self.db_cursor.execute(query, tuple(values))

        def search(self, **criteria):
            clauses = []
            values = []

            for clause, value in criteria.items():
                if isinstance(value, list): # Tags
                    clauses.append(f"{clause} && %s") # PostgreSQL overlap array operator????
                    values.append(value)
                else:
                    clauses.append(f"{clause} = %s")
                    values.append(value)

    def close_connection(self):
        self.db_cursor.close()
        self.db_conn.close()

songg_id = SongStorage().add_song("C:/Users/anaun/Downloads/sample-file-1.wav", "New Artist", "csdc", datetime.datetime.now(), ["csdc", "cscdsc"])
#SongStorage().delete_song(6)
SongStorage().modify_data(1, artist="New Artist", song_name="New Song Name")

SongStorage().close_connection()

#Loguri rulare program?????????????????????????????????????????????????????????????????????