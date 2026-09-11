from src.db import get_connection


def init_feedback_table():
    """Creates a table to store usefulness ratings for each alert sent."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_key TEXT NOT NULL,
            rating TEXT CHECK(rating IN ('useful', 'not_useful')),
            rated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def rate_alert(ticket_key, rating):
    """
    Records a usefulness rating for a specific ticket's alert.
    rating must be 'useful' or 'not_useful'.
    """
    if rating not in ("useful", "not_useful"):
        raise ValueError("rating must be 'useful' or 'not_useful'")

    init_feedback_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alert_feedback (ticket_key, rating) VALUES (?, ?)",
        (ticket_key, rating)
    )
    conn.commit()
    conn.close()


def get_alert_precision():
    """
    Returns the % of rated alerts marked 'useful' — this is the
    'Alert precision' metric from the proposal's success metrics table.
    """
    init_feedback_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alert_feedback WHERE rating = 'useful'")
    useful = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM alert_feedback")
    total = cursor.fetchone()[0]
    conn.close()

    if total == 0:
        return None
    return round(useful / total * 100, 1)


if __name__ == "__main__":
    # Simulate a team member rating a few alerts, for demo purposes
    rate_alert("KAN-6", "useful")
    rate_alert("KAN-7", "useful")
    rate_alert("KAN-11", "not_useful")

    precision = get_alert_precision()
    print(f"Alert precision so far: {precision}%")