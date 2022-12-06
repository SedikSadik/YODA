-- Create Database with these commands if database deleted
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL
);

CREATE TABLE saved (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    owner_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,
    media_type TEXT NOT NULL,
    process_type TEXT NOT NULL,
    upload_time TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE UNIQUE INDEX username ON users (username);

CREATE UNIQUE INDEX id ON saved(id);

-- Insert into the saved files table