import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.redaction import redact_text, redact_ticket


def test_email_is_redacted():
    text = "Contact me at jane.doe@example.com for details"
    result = redact_text(text)
    assert "jane.doe@example.com" not in result
    assert "[REDACTED_EMAIL]" in result


def test_phone_is_redacted():
    text = "Call me at 9876543210 tomorrow"
    result = redact_text(text)
    assert "9876543210" not in result
    assert "[REDACTED_PHONE]" in result


def test_text_without_pii_is_unchanged():
    text = "Login page throwing 500 error"
    result = redact_text(text)
    assert result == text


def test_empty_text_does_not_crash():
    assert redact_text("") == ""
    assert redact_text(None) is None


def test_redact_ticket_preserves_structure():
    ticket = {
        "key": "TEST-1",
        "fields": {"summary": "Reach me at test@example.com", "priority": {"name": "High"}}
    }
    result = redact_ticket(ticket)
    assert result["key"] == "TEST-1"
    assert "[REDACTED_EMAIL]" in result["fields"]["summary"]
    assert result["fields"]["priority"]["name"] == "High"  # untouched fields stay intact