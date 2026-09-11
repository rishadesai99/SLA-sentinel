import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tempfile
from src import db as db_module
from src.feedback import rate_alert, get_alert_precision, init_feedback_table

TEST_DB_PATH = None


def setup_function():
    global TEST_DB_PATH
    fd, TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_module.DB_PATH = TEST_DB_PATH


def teardown_function():
    if TEST_DB_PATH and os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_precision_with_no_ratings_returns_none():
    init_feedback_table()
    assert get_alert_precision() is None


def test_precision_calculates_correctly():
    rate_alert("T-1", "useful")
    rate_alert("T-2", "useful")
    rate_alert("T-3", "not_useful")
    assert get_alert_precision() == 66.7


def test_invalid_rating_raises_error():
    try:
        rate_alert("T-4", "maybe")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass