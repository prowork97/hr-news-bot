import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS salary_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specialization TEXT NOT NULL,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_news(title: str, source_url: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO news (title, source_url) VALUES (?, ?)", (title, source_url))
    conn.commit()
    conn.close()

def get_all_urls() -> set:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT source_url FROM news").fetchall()
    conn.close()
    return {r[0] for r in rows if r[0]}

def get_all_titles() -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT title FROM news ORDER BY created_at DESC LIMIT 200").fetchall()
    conn.close()
    return [r[0] for r in rows]
