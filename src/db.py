import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sla_sentinel.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Creates the tickets table if it doesn't already exist.
    Safe to run every time — won't wipe existing data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_key TEXT NOT NULL,
            summary TEXT,
            priority TEXT,
            elapsed_hrs REAL,
            sla_hrs REAL,
            pct_of_sla_used REAL,
            status TEXT,
            run_timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_scored_tickets(scored_tickets):
    """
    Saves a list of scored ticket dicts (from risk_engine.score_all_tickets)
    into the database. Each run adds new rows — this builds up history over time.
    """
    conn = get_connection()
    cursor = conn.cursor()
    for t in scored_tickets:
        cursor.execute("""
            INSERT INTO ticket_scores
            (ticket_key, summary, priority, elapsed_hrs, sla_hrs, pct_of_sla_used, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            t["key"], t["summary"], t["priority"],
            t["elapsed_hrs"], t["sla_hrs"], t["pct_of_sla_used"], t["status"]
        ))
    conn.commit()
    conn.close()


def fetch_all_runs():
    """Returns every saved row, most recent first. Useful for checking history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ticket_scores ORDER BY run_timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")