-- Manual SQL migration for event_embeddings table
-- This requires pgvector extension to be installed first in PostgreSQL
-- Installation steps:
--   1. Install pgvector: sudo apt-get install postgresql-14-pgvector
--   2. Enable extension: CREATE EXTENSION IF NOT EXISTS vector;
--   3. Run this SQL file to create the table

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS event_embeddings (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL UNIQUE REFERENCES events(id) ON DELETE CASCADE,
    embedding VECTOR(384) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_event_embeddings_event_id ON event_embeddings(event_id);
