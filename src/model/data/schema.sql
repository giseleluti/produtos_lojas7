DROP TABLE IF EXISTS produtos;

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    image TEXT NOT NULL
);
