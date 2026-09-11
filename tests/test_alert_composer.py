import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.alert_composer import compose_alert


def test_alert_is_none_when_should_not_alert():
    ticket = {"key": "T-1", "summary": "test", "priority": "Low", "pct_of_sla_used": 10.0}
    escalation = {"should_alert": False, "notify_tier": None, "message_prefix": None}
    result = compose_alert(ticket, escalation, "https://example.atlassian.net")
    assert result is None


def test_alert_contains_key_details():
    ticket = {"key": "T-2", "summary": "Server down", "priority": "Highest", "pct_of_sla_used": 150.0}
    escalation = {"should_alert": True, "notify_tier": "L2", "message_prefix": "SLA BREACHED"}
    result = compose_alert(ticket, escalation, "https://example.atlassian.net")

    assert "T-2" in result
    assert "Server down" in result
    assert "L2" in result
    assert "https://example.atlassian.net/browse/T-2" in result