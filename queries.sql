-- These queries were used during database configuration.
CREATE TABLE users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL, firstname TEXT, lastname TEXT);

INSERT INTO users (username, password, email) VALUES ('johnnytest', 'password123', 'johnnytest@example.com');
INSERT INTO users (username, password, email) VALUES ('sillymelon12', 'password456', 'sillymelon12@example.com');