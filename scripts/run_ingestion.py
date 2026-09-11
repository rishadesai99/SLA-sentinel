import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.jira_client import fetch_open_tickets, SITE
from src.redaction import redact_ticket
from src.risk_engine import load_sla_policy, score_all_tickets
from src.escalation import load_escalation_policy, get_escalations_for_all
from src.alert_composer import compose_alerts_for_all
from src.db import init_db, save_scored_tickets


def main():
    print("SLA Sentinel - Phase 0/1: Breach Detection + Alerts")
    print("=" * 50)

    init_db()

    tickets = fetch_open_tickets()
    tickets = [redact_ticket(t) for t in tickets]

    sla_policy = load_sla_policy()
    scored = score_all_tickets(tickets, sla_policy)

    print(f"\nFetched {len(tickets)} open tickets, scored {len(scored)}\n")
    print(f"{'KEY':<8}{'PRIORITY':<10}{'% SLA USED':<12}{'STATUS':<10}SUMMARY")
    print("-" * 80)
    for r in scored:
        print(f"{r['key']:<8}{r['priority']:<10}{r['pct_of_sla_used']:<12}{r['status']:<10}{r['summary']}")

    breached = [r for r in scored if r["status"] == "BREACHED"]
    at_risk = [r for r in scored if r["status"] == "AT RISK"]
    print(f"\nSummary: {len(breached)} breached, {len(at_risk)} at risk, {len(scored) - len(breached) - len(at_risk)} OK")

    save_scored_tickets(scored)
    print(f"Saved {len(scored)} scored tickets to database.")

    escalation_policy = load_escalation_policy()
    scored_with_escalation = get_escalations_for_all(scored, escalation_policy)

    from src.dedup import filter_new_alerts
    new_alerts_only = filter_new_alerts(scored_with_escalation, window_hours=1)

    from src.retrieval import load_historical_tickets, build_ticket_index
    historical_tickets = load_historical_tickets()
    retrieval_data = build_ticket_index(historical_tickets)

    alerts = compose_alerts_for_all(new_alerts_only, SITE, retrieval_data=retrieval_data)

    print("\n" + "=" * 50)
    print(f"ALERTS ({len(alerts)} to send)")
    print("=" * 50)
    for a in alerts:
        print(a)
        print("-" * 50)

    from src.slack_client import send_all_alerts
    sent_count = send_all_alerts(alerts)
    print(f"\nPosted {sent_count}/{len(alerts)} alerts to Slack.")


if __name__ == "__main__":
    main()
    