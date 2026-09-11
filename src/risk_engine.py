import yaml
from datetime import datetime, timezone


def load_sla_policy(path="config/sla_policy.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def hours_since_created(created_str):
    """
    Jira gives timestamps like '2026-08-13T17:44:02.895+0530'.
    This converts that into 'how many hours ago was this created'.
    """
    created = datetime.fromisoformat(created_str)
    now = datetime.now(created.tzinfo)
    return (now - created).total_seconds() / 3600


def score_ticket(ticket, policy):
    """
    Takes one raw Jira ticket dict and the SLA policy dict.
    Returns a scored summary, or None if the ticket is already resolved.
    """
    fields = ticket["fields"]

    if fields["resolutiondate"]:
        return None  # already resolved — not our concern

    priority = fields["priority"]["name"] if fields["priority"] else "None"
    sla_hours = policy["sla_hours"].get(priority, 24)  # fallback: 24hrs if unknown priority

    elapsed = hours_since_created(fields["created"])
    pct_used = elapsed / sla_hours

    thresholds = policy["risk_thresholds"]
    if pct_used >= thresholds["breached"]:
        status = "BREACHED"
    elif pct_used >= thresholds["at_risk"]:
        status = "AT RISK"
    else:
        status = "OK"

    return {
        "key": ticket["key"],
        "summary": fields["summary"],
        "priority": priority,
        "elapsed_hrs": round(elapsed, 1),
        "sla_hrs": sla_hours,
        "pct_of_sla_used": round(pct_used * 100, 1),
        "status": status,
    }


def score_all_tickets(tickets, policy=None):
    if policy is None:
        policy = load_sla_policy()
    scored = [score_ticket(t, policy) for t in tickets]
    scored = [s for s in scored if s is not None]
    scored.sort(key=lambda x: x["pct_of_sla_used"], reverse=True)
    return scored


if __name__ == "__main__":
    from src.jira_client import fetch_open_tickets

    tickets = fetch_open_tickets()
    policy = load_sla_policy()
    results = score_all_tickets(tickets, policy)

    print(f"{'KEY':<8}{'PRIORITY':<10}{'% SLA USED':<12}{'STATUS':<10}SUMMARY")
    for r in results:
        print(f"{r['key']:<8}{r['priority']:<10}{r['pct_of_sla_used']:<12}{r['status']:<10}{r['summary']}")