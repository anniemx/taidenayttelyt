CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    image BLOB
);

CREATE TABLE exhibitions (
    id INTEGER PRIMARY KEY,
    title TEXT,
    place TEXT,
    time TEXT,
    location TEXT,
    description TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE exhibition_classes (
    id INTEGER PRIMARY KEY,
    exhibition_id INTEGER REFERENCES exhibitions,
    title TEXT,
    value TEXT
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    sent_at TEXT,
    user_id INTEGER REFERENCES users,
    evaluation INTEGER,
    exhibition_id INTEGER REFERENCES exhibitions
);

CREATE INDEX idx_exhibitions_comments ON comments (exhibition_id);