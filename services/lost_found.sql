CREATE TABLE IF NOT EXISTS users
(
    id SERIAL PRIMARY KEY,
    telegram_id TEXT UNIQUE NOT NULL,
    username VARCHAR(100),
    full_name VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS items
(
    id SERIAL PRIMARY KEY,
    owner_id BIGINT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT NOT NULL,
    photo_file_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'returned')),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS claims
(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE (user_id, item_id)
);
