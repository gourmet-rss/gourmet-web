CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE users (
    id UUID PRIMARY KEY
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    embedding VECTOR(768) -- Assuming a 768-dimensional embedding, adjust as needed
);
