# db.py
import sqlite3
from datetime import datetime
import json
from typing import Any, Dict

DB_PATH = "ats_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        filename TEXT,
        resume_text TEXT,
        analysis_json TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_analysis(user_id: str, filename: str, resume_text: str, analysis: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO analyses (user_id, filename, resume_text, analysis_json, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, filename, resume_text, json.dumps(analysis), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
