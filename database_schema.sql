-- Database schema for Personal Blogging Platform API
-- Compatible with PostgreSQL (including Neon)
-- This is provided for reference / manual setup.
-- Prisma migrations (prisma/migrations) are the source of truth and
-- will create these tables automatically via `npx prisma migrate deploy`.

-- Enable UUID generation (Neon/Postgres 13+ supports gen_random_uuid() via pgcrypto)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================
-- Table: users
-- ============================
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(255) NOT NULL,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- Table: posts
-- ============================
CREATE TABLE IF NOT EXISTS posts (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title      VARCHAR(255) NOT NULL,
    content    TEXT NOT NULL,
    author_id  UUID NOT NULL,
    created_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_posts_author
        FOREIGN KEY (author_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);

-- Index to speed up lookups of posts by author
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts (author_id);

-- Index to speed up sorting posts by creation date (used by GET /posts)
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts (created_at DESC);
