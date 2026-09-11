import yaml


def load_escalation_policy(path="config/escalation_policy.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_escalation(scored_ticket, policy):
    """
    Takes one scored ticket (from risk_engine) and the escalation policy.
    Returns a dict describing what to do: notify_tier, message_prefix, and
    whether an alert should be sent at all.
    """
    status = scored_ticket["status"]
    rules = policy["escalation_rules"].get(status)

    if rules is None or rules["notify_tier"] is None:
        return {
            "should_alert": False,
            "notify_tier": None,
            "message_prefix": None,
        }

    return {
        "should_alert": True,
        "notify_tier": rules["notify_tier"],
        "message_prefix": rules["message_prefix"],
    }


def get_escalations_for_all(scored_tickets, policy=None):
    if policy is None:
        policy = load_escalation_policy()
    return [
        {**ticket, "escalation": get_escalation(ticket, policy)}
        for ticket in scored_tickets
    ]


if __name__ == "__main__":
    policy = load_escalation_policy()

    sample_tickets = [
        {"key": "TEST-1", "status": "BREACHED", "priority": "Highest", "summary": "Sample breach"},
        {"key": "TEST-2", "status": "AT RISK", "priority": "High", "summary": "Sample at risk"},
        {"key": "TEST-3", "status": "OK", "priority": "Low", "summary": "Sample ok"},
    ]

    results = get_escalations_for_all(sample_tickets, policy)
    for r in results:
        esc = r["escalation"]
        print(f"{r['key']:<8} status={r['status']:<10} should_alert={esc['should_alert']:<6} tier={esc['notify_tier']}")