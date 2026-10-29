"""
Database management module for Intelligent Hostel Complaint Management System.
Supports SQLite (zero-config local default) and PostgreSQL.
Includes automated schema creation and demo seed data.
"""

import sqlite3
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

DB_FILE = os.environ.get("DB_FILE", os.path.join(os.path.dirname(__file__), "hostel.db"))


def hash_password(password: str) -> str:
    """Generate SHA256 hashed password with salt for secure storage."""
    salt = "hostel_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash."""
    return hash_password(plain_password) == hashed_password


def get_db():
    """Get SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all required tables, indexes, and seed realistic demo records."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password TEXT NOT NULL,
        type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Block table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS block (
        block_id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_name TEXT NOT NULL,
        description TEXT
    );
    """)

    # 3. Student table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        student_id INTEGER PRIMARY KEY,
        block_id INTEGER,
        usn TEXT,
        room TEXT,
        FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
    );
    """)

    # 4. Warden table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warden (
        warden_id INTEGER PRIMARY KEY,
        block_id INTEGER,
        FOREIGN KEY (warden_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
    );
    """)

    # 5. Complaint table (Enhanced with AI priority and categorization fields)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        block_id INTEGER,
        student_id INTEGER,
        description TEXT NOT NULL,
        room TEXT,
        is_completed BOOLEAN DEFAULT 0,
        status TEXT DEFAULT 'PENDING',
        priority TEXT DEFAULT 'MEDIUM',
        priority_score INTEGER DEFAULT 50,
        category TEXT DEFAULT 'General',
        urgency_reason TEXT,
        suggested_action TEXT,
        sla_hours INTEGER DEFAULT 24,
        ai_engine TEXT DEFAULT 'Embedded Local NLP Engine',
        warden_notes TEXT,
        media_url TEXT,
        media_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        assigned_at TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
        FOREIGN KEY (block_id) REFERENCES block(block_id) ON DELETE SET NULL
    );
    """)

    # Automatic migration for existing databases: ensure media columns exist
    cursor.execute("PRAGMA table_info(complaint);")
    existing_cols = [col[1] for col in cursor.fetchall()]
    if "media_url" not in existing_cols:
        cursor.execute("ALTER TABLE complaint ADD COLUMN media_url TEXT;")
    if "media_type" not in existing_cols:
        cursor.execute("ALTER TABLE complaint ADD COLUMN media_type TEXT;")

    # Indexes for high performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_priority ON complaint(priority_score DESC);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_student ON complaint(student_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaint(status);")

    # Seed blocks if empty
    cursor.execute("SELECT COUNT(*) FROM block;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO block (block_name, description) VALUES ('Block A (North Wing)', 'Undergraduate Boys Residence');")
        cursor.execute("INSERT INTO block (block_name, description) VALUES ('Block B (South Wing)', 'Undergraduate Girls Residence');")
        cursor.execute("INSERT INTO block (block_name, description) VALUES ('Block C (Tech Wing)', 'Postgraduate & Research Block');")

    # Seed demo users if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        # Official Warden Account
        warden_pass = hash_password("warden123")
        cursor.execute(
            "INSERT INTO users (full_name, email, phone, password, type) VALUES (?, ?, ?, ?, ?);",
            ("Chief Warden", "warden@hostel.edu", "+91 98765 00001", warden_pass, "warden")
        )
        warden_id = cursor.lastrowid
        cursor.execute("INSERT INTO warden (warden_id, block_id) VALUES (?, ?);", (warden_id, 1))

        # Official Resident Accounts
        student_pass = hash_password("student123")
        students_seed = [
            ("Pranil Shah", "student@hostel.edu", "+91 98201 26507", "26070126505", 1, "101"),
            ("Ansh Gajjar", "ansh@hostel.edu", "+91 98201 26508", "26070126508", 1, "102"),
            ("Meet Dagade", "meet@hostel.edu", "+91 98201 26505", "26070126505", 1, "103"),
            ("Karthik Bocca", "karthik@hostel.edu", "+91 98201 26219", "25070126219", 2, "204")
        ]
        for name, email, phone, usn, block_id, room in students_seed:
            cursor.execute(
                "INSERT INTO users (full_name, email, phone, password, type) VALUES (?, ?, ?, ?, ?);",
                (name, email, phone, student_pass, "student")
            )
            s_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO student (student_id, block_id, usn, room) VALUES (?, ?, ?, ?);",
                (s_id, block_id, usn, room)
            )

    conn.commit()
    conn.close()


# Database Schema SQL export for documentation and external tools
DATABASE_SCHEMA_SQL = """
-- Intelligent Hostel Complaint Management System
-- Schema Definition with AI Priority & Urgency Features

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('student', 'warden', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS block (
    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS student (
    student_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL,
    usn TEXT,
    room TEXT
);

CREATE TABLE IF NOT EXISTS warden (
    warden_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS complaint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    block_id INTEGER REFERENCES block(block_id) ON DELETE SET NULL,
    student_id INTEGER REFERENCES student(student_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    room TEXT,
    is_completed BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'RESOLVED', 'REJECTED')),
    priority TEXT DEFAULT 'MEDIUM' CHECK(priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    priority_score INTEGER DEFAULT 50,
    category TEXT DEFAULT 'General',
    urgency_reason TEXT,
    suggested_action TEXT,
    sla_hours INTEGER DEFAULT 24,
    ai_engine TEXT DEFAULT 'Embedded Local NLP Prioritizer',
    warden_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_complaint_priority ON complaint(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_complaint_student ON complaint(student_id);
CREATE INDEX IF NOT EXISTS idx_complaint_status ON complaint(status);
"""
