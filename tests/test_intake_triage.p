import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intake_triage import check_ticket_completeness


def test_vague_ticket_flags_missing_fields():
    result = check_ticket_completeness("Login page throwing 500 error")
    assert result["is_complete"] is False
    assert "steps_to_reproduce" in result["missing_fields"]


def test_detailed_ticket_is_mostly_complete():
    result = check_ticket_completeness(
        "App crashes on iOS, error 4042, happens since yesterday 3pm"
    )
    assert "error_code" not in result["missing_fields"]
    assert "environment" not in result["missing_fields"]
    assert "timestamp" not in result["missing_fields"]