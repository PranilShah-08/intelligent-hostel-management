-- Intelligent Hostel Complaint Management System
-- Database Schema with AI Urgency & Priority Triage Extensions
-- Compatible with PostgreSQL & SQLite

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('student', 'warden', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Hostel Blocks Table
CREATE TABLE IF NOT EXISTS block (
    block_id SERIAL PRIMARY KEY,
    block_name TEXT NOT NULL,
    description TEXT
);

-- 3. Student Details Table
CREATE TABLE IF NOT EXISTS student (
    student_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL,
    usn TEXT,
    room TEXT
);

-- 4. Warden Details Table
CREATE TABLE IF NOT EXISTS warden (
    warden_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL
);

-- 5. Complaints Table with AI Priority & Urgency Scoring
CREATE TABLE IF NOT EXISTS complaint (
    id SERIAL PRIMARY KEY,
    name TEXT,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL,
    student_id INTEGER REFERENCES student(student_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    room TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED')),
    priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK(priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    priority_score INTEGER DEFAULT 50, -- 1 to 100 numerical urgency score
    category VARCHAR(50) DEFAULT 'General',
    urgency_reason TEXT,              -- AI rationale on why this priority was given
    suggested_action TEXT,            -- Recommended immediate warden/technician mitigation
    sla_hours INTEGER DEFAULT 24,     -- Target response time SLA
    ai_engine VARCHAR(100) DEFAULT 'Local Embedded NLP Engine',
    warden_notes TEXT,
    media_url TEXT,                   -- URL or relative path to attached photo or video
    media_type VARCHAR(20),           -- 'image' or 'video'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_complaint_priority ON complaint(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_complaint_student ON complaint(student_id);
CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaint(status);
CREATE INDEX IF NOT EXISTS idx_complaint_category ON complaint(category);
