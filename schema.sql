-- ============================================================
-- schema.sql  –  Smart Task Management System
-- Run this ONCE to set up the database from scratch
-- ============================================================

-- 1. Create database & user (run as postgres superuser)
-- psql -U postgres -f schema.sql

CREATE DATABASE taskdb;
CREATE USER taskuser WITH PASSWORD 'taskpassword';
GRANT ALL PRIVILEGES ON DATABASE taskdb TO taskuser;

-- 2. Connect to taskdb, then create tables
\c taskdb;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    priority    VARCHAR(20)  NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('low', 'medium', 'high')),
    status      VARCHAR(30)  NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending', 'in_progress', 'completed')),
    created_at  TIMESTAMP DEFAULT NOW(),
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_tasks_user_id  ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);

-- Grant table permissions to taskuser
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA public TO taskuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO taskuser;
