import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import sqlite3
from src import db as db_module
from src.dedup import filter_new_alerts, was_recently_alerted, log_alert_sent, init_alert_log_table

import tempfile

TEST_DB_PATH = None

def setup_function():
    """Runs before each test — point the db module at a fresh temporary
    file-based database, so tests never touch your real sla_sentinel.db,
    but still share state properly across connections (unlike :memory:)."""
    global TEST_DB_PATH
    fd, TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_module.DB_PATH = TEST_DB_PATH


def teardown_function():
    """Runs after each test — clean up the temp file."""
    if TEST_DB_PATH and os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_ticket_not_alerted_before_returns_false():
    init_alert_log_table()
    assert was_recently_alerted("FAKE-1") is False


def test_ticket_alerted_recently_returns_true():
    init_alert_log_table()
    log_alert_sent("FAKE-2")
    assert was_recently_alerted("FAKE-2") is True


def test_filter_new_alerts_skips_already_alerted():
    init_alert_log_table()
    tickets = [
        {"key": "FAKE-3", "escalation": {"should_alert": True}},
        {"key": "FAKE-4", "escalation": {"should_alert": True}},
    ]
    first_pass = filter_new_alerts(tickets)
    assert len(first_pass) == 2  # both new, both pass

    second_pass = filter_new_alerts(tickets)
    assert len(second_pass) == 0  # both already alerted, both skipped