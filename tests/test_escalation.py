import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.escalation import get_escalation

POLICY = {
    "escalation_rules": {
        "BREACHED": {"notify_tier": "L2", "message_prefix": "SLA BREACHED"},
        "AT RISK": {"notify_tier": "L1", "message_prefix": "AT RISK"},
        "OK": {"notify_tier": None, "message_prefix": None},
    }
}


def test_breached_escalates_to_l2():
    ticket = {"key": "T-1", "status": "BREACHED"}
    result = get_escalation(ticket, POLICY)
    assert result["should_alert"] is True
    assert result["notify_tier"] == "L2"


def test_at_risk_escalates_to_l1():
    ticket = {"key": "T-2", "status": "AT RISK"}
    result = get_escalation(ticket, POLICY)
    assert result["should_alert"] is True
    assert result["notify_tier"] == "L1"


def test_ok_does_not_alert():
    ticket = {"key": "T-3", "status": "OK"}
    result = get_escalation(ticket, POLICY)
    assert result["should_alert"] is False
    assert result["notify_tier"] is None
    