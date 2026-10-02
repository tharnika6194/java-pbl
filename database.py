import sqlite3
import os
import json
from datetime import datetime

# Resolve absolute path to the database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'startup_validator.db')

def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes tables and seeds default user and sample startup data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. startup_ideas table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS startup_ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        startup_name TEXT NOT NULL,
        idea_description TEXT NOT NULL,
        problem_statement TEXT,
        target_customers TEXT,
        industry TEXT,
        target_market TEXT,
        business_model TEXT,
        initial_budget TEXT,
        competitors TEXT,
        unique_features TEXT,
        technology_used TEXT,
        revenue_model TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')

    # 3. validation_reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS validation_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startup_id INTEGER NOT NULL,
        overall_score INTEGER NOT NULL,
        validation_status TEXT NOT NULL,
        summary TEXT,
        problem_analysis TEXT,
        customer_analysis TEXT,
        market_analysis TEXT,
        competitor_analysis TEXT,
        uvp_analysis TEXT,
        business_model_analysis TEXT,
        cost_estimation TEXT,
        risk_analysis TEXT,
        scalability_analysis TEXT,
        tech_feasibility TEXT,
        roadmap TEXT,
        pdf_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (startup_id) REFERENCES startup_ideas(id) ON DELETE CASCADE
    )
    ''')

    # 4. analysis_scores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        startup_id INTEGER NOT NULL,
        problem_fit INTEGER NOT NULL,
        market_potential INTEGER NOT NULL,
        competition INTEGER NOT NULL,
        business_model INTEGER NOT NULL,
        revenue_potential INTEGER NOT NULL,
        scalability INTEGER NOT NULL,
        tech_feasibility INTEGER NOT NULL,
        risk_score INTEGER NOT NULL,
        overall_score INTEGER NOT NULL,
        FOREIGN KEY (report_id) REFERENCES validation_reports(id) ON DELETE CASCADE,
        FOREIGN KEY (startup_id) REFERENCES startup_ideas(id) ON DELETE CASCADE
    )
    ''')

    # 5. recommendations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        startup_id INTEGER NOT NULL,
        recommendation_order INTEGER NOT NULL,
        category TEXT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        impact TEXT DEFAULT 'High',
        FOREIGN KEY (report_id) REFERENCES validation_reports(id) ON DELETE CASCADE,
        FOREIGN KEY (startup_id) REFERENCES startup_ideas(id) ON DELETE CASCADE
    )
    ''')

    # Ensure default demo user exists
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'Founder Demo', 'demo@aistartupvalidator.local')")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at", DB_PATH)
