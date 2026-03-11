-- Smart File Organizer Pro - PostgreSQL Schema
-- Note: This schema is automatically generated and managed by SQLAlchemy. 
-- This file is provided for reference purposes.

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE file_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    original_path TEXT NOT NULL,
    current_path TEXT NOT NULL,
    filename TEXT NOT NULL,
    extension VARCHAR(50),
    size BIGINT,
    file_hash VARCHAR(64),
    category VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITHOUT TIME ZONE,
    last_accessed TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    path_scanned TEXT NOT NULL,
    files_found INTEGER DEFAULT 0,
    total_size BIGINT DEFAULT 0,
    start_time TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITHOUT TIME ZONE,
    status VARCHAR(50) DEFAULT 'in_progress'
);

CREATE TABLE organization_rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    condition_type VARCHAR(50) NOT NULL,
    condition_value TEXT NOT NULL,
    target_folder TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE duplicates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    hash_value VARCHAR(64) NOT NULL,
    file_paths TEXT, -- Stored as JSON string
    total_wasted_space BIGINT DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    details TEXT,
    file_path TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scheduled_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_type VARCHAR(50) NOT NULL,
    target_directory TEXT,
    cron_hour VARCHAR(10) DEFAULT '0',
    cron_minute VARCHAR(10) DEFAULT '0',
    is_active BOOLEAN DEFAULT TRUE,
    last_run TIMESTAMP WITHOUT TIME ZONE,
    next_run TIMESTAMP WITHOUT TIME ZONE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
