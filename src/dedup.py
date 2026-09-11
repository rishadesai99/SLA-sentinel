from datetime import datetime, timedelta, UTC
from src.db import get_connection


def init_alert_log_table():
    """Creates a table to track when each ticket was last alerted on."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_key TEXT NOT NULL,
            alerted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def was_recently_alerted(ticket_key, window_hours=1):
    """
    Returns True if this ticket was already alerted on within the last
    `window_hours` hours, so we know to skip it this time.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cutoff = (datetime.now(UTC) - timedelta(hours=window_hours)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        SELECT COUNT(*) FROM alert_log
        WHERE ticket_key = ? AND alerted_at >= ?
    """, (ticket_key, cutoff))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def log_alert_sent(ticket_key):
    """Records that we just sent an alert for this ticket, right now."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alert_log (ticket_key) VALUES (?)", (ticket_key,))
    conn.commit()
    conn.close()


def filter_new_alerts(scored_tickets_with_escalation, window_hours=1):
    """
    Takes the list of tickets that WOULD alert, and returns only the ones
    that haven't already alerted recently. Also logs the ones that pass.
    """
    init_alert_log_table()
    filtered = []
    for ticket in scored_tickets_with_escalation:
        if not ticket["escalation"]["should_alert"]:
            continue
        if was_recently_alerted(ticket["key"], window_hours):
            continue  # skip, already alerted recently
        filtered.append(ticket)
        log_alert_sent(ticket["key"])
    return filtered