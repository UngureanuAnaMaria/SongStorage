# SongStorage Tool

## Description  
The **SongStorage** tool is a simple solution for managing music files (MP3, WAV, etc.) within a storage folder. It allows users to add, modify, delete, search, and organize songs while also storing metadata about each track in a database. The tool provides functionality for operations like adding songs, modifying metadata, creating playlists, and more. 

A **Graphical User Interface (GUI)** is provided using **Tkinter**, allowing users to perform all operations through an easy-to-use interface without needing to use the command line.

The main window displays a real-time list of all songs and their metadata, and users can interact with buttons to open new windows for various operations such as adding songs, modifying metadata, and searching.

## Features

### 1. **Add Song**  
Allows users to upload a song file and store it in the designated storage folder. Alongside the file, metadata is saved to the database, including the song's name, artist, release date, and tags.  
**Input**: File path of the song (MP3, WAV, etc.) and metadata.  
**Output**: Unique ID for the song in the database.

### 2. **Delete Song**  
Deletes both the song file and its associated metadata from the database using the song’s ID.  
**Input**: ID of the song in the database.  
**Output**: Success or error message.

### 3. **Modify Metadata**  
Allows users to update the metadata for a specific song based on its unique ID.  
**Input**: ID of the song and the updated metadata.  
**Output**: Confirmation of the update or error message.

### 4. **Create SaveList**  
Enables users to create a playlist archive based on specific search criteria (e.g., artist, song format). The output is an archive containing the selected songs.  
**Input**: Path for the archive output and search criteria (e.g., artist=Queen, format=mp3).  
**Output**: An archive file containing the selected songs.

### 5. **Search**  
Searches for songs based on user-defined criteria (e.g., artist, song format) and returns metadata for matching songs.  
**Input**: Search criteria (e.g., artist=Queen, format=mp3).  
**Output**: List of songs that match the search criteria.

### 6. **Play**  
Provides the ability to play songs from the storage using third-party libraries for media playback.  
**Input**: ID of the song to be played.  
**Output**: Audio playback.

## Graphical User Interface (GUI)
The tool provides a **Tkinter**-based GUI for users who prefer not to interact with the command line. The main window displays a **real-time list** of all songs and their metadata. This list automatically updates as songs are added, deleted, or modified. 

### Features of the GUI:
- **Main Window**: A list of all songs and their metadata (artist, title, release date, tags) that updates in real time.
- **Buttons**: Various buttons are available for opening new windows where users can:
  - Add a new song.
  - Modify the metadata of a song.
  - Search for songs by criteria.
  - Delete songs.
  - Play song.
  - Create save list.
- **Windows**: Each action (e.g., add song, modify metadata) opens a new window for a seamless user experience.

## Code Documentation
The **SongStorage** project is thoroughly documented to help you understand the code structure and how to use the functions in your own projects. The documentation includes:

- **Function Definitions**: Each function is documented with a description of its purpose, parameters, and output.
- **Classes and Methods**: The classes used within the tool are fully documented, including their attributes and methods.
- **Error Handling**: Detailed information about possible errors and exceptions, with instructions on how to handle them.
- **GUI Flow**: The flow of the graphical interface is described, explaining how users interact with the various windows and buttons.

The full code documentation is available within the source code itself, with docstrings provided for each function and class. You can explore the documentation to understand how the tool is structured and how to extend it if needed.

## Logs & Errors  
The tool generates logs for each operation performed, which can be helpful for troubleshooting. In case of any issues (e.g., missing file, invalid ID), detailed error messages will be provided.

## Technologies Used
- Python
- Tkinter for GUI
- Third-party libraries for media playback
- SQLite or PostgreSQL for metadata storage

## Installation  
To use the SongStorage tool, clone this repository and install the necessary dependencies:

```bash
git clone https://github.com/UngureanuAnaMaria/SongStorage.git
cd SongStorage
pip install -r requirements.txt

