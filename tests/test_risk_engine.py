import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.risk_engine import score_ticket

POLICY = {
    "sla_hours": {"Highest": 4, "High": 8, "Medium": 24, "Low": 72, "None": 24},
    "risk_thresholds": {"breached": 1.0, "at_risk": 0.7}
}


def make_ticket(priority, hours_ago, resolved=False):
    from datetime import datetime, timedelta, timezone
    created = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return {
        "key": "TEST-1",
        "fields": {
            "summary": "test ticket",
            "priority": {"name": priority} if priority else None,
            "created": created.isoformat(),
            "resolutiondate": "2026-01-01T00:00:00.000+0000" if resolved else None,
        }
    }


def test_breached_ticket_flagged():
    ticket = make_ticket("Highest", hours_ago=5)
    result = score_ticket(ticket, POLICY)
    assert result["status"] == "BREACHED"


def test_fresh_ticket_is_ok():
    ticket = make_ticket("Highest", hours_ago=1)
    result = score_ticket(ticket, POLICY)
    assert result["status"] == "OK"


def test_resolved_ticket_is_skipped():
    ticket = make_ticket("Highest", hours_ago=10, resolved=True)
    result = score_ticket(ticket, POLICY)
    assert result is None