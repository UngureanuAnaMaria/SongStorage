import psycopg2

# Realizare conexiunii
conn = psycopg2.connect(
    database="postgres", # Baza de date implicita
    user='postgres',
    password='password',
    host='localhost',
    port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'SongStorage'")
exists = cursor.fetchone()

if not exists:
    cursor.execute('CREATE DATABASE "SongStorage";')
    print("Database 'SongStorage' has been created successfully!")
else:
    print("Database 'SongStorage' already exists.")

cursor.close()
conn.close()


db_conn = psycopg2.connect(
    database="SongStorage",
    user='postgres',
    password='password',
    host='localhost',
    port='5432'
)

db_conn.autocommit = True
db_cursor = db_conn.cursor()

db_cursor.execute('''
       SELECT EXISTS (
           SELECT 1
           FROM information_schema.tables
           WHERE table_name = 'songs'
       );
   ''')
table_exists = db_cursor.fetchone()[0]

if not table_exists:
    db_cursor.execute('''
        CREATE TABLE songs (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL UNIQUE,
            artist VARCHAR(255) NOT NULL,
            song_name VARCHAR(255) NOT NULL,
            release_date DATE,
            tags TEXT[]
        );
    ''')
    print("Table 'songs' has been created successfully!")
else:
    print("Table 'songs' already exists.")

db_cursor.close()
db_conn.close()

