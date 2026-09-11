def compose_alert(scored_ticket, escalation_info, jira_site, similar_tickets=None):
    """
    Takes a scored ticket + its escalation decision, returns a formatted
    alert message string. If similar_tickets is provided, enriches the
    alert with retrieved historical context.
    """
    if not escalation_info["should_alert"]:
        return None

    prefix = escalation_info["message_prefix"]
    tier = escalation_info["notify_tier"]
    ticket_url = f"{jira_site}/browse/{scored_ticket['key']}"

    message = (
        f"[{prefix}] {scored_ticket['key']}: {scored_ticket['summary']}\n"
        f"  Priority: {scored_ticket['priority']} | "
        f"SLA used: {scored_ticket['pct_of_sla_used']}% | "
        f"Notify: {tier}\n"
        f"  Link: {ticket_url}"
    )

    if similar_tickets:
        message += "\n  Similar past issues:"
        for s in similar_tickets:
            message += f"\n    - [{s['key']}] {s['summary']} (similarity: {s['similarity_score']})"
            message += f"\n      Resolved by: {s['resolution']}"

    routing = scored_ticket.get("routing")
    if routing and routing.get("recommended_assignee"):
        message += f"\n  Recommended assignee: {routing['recommended_assignee']} (confidence: {routing['confidence']}%)"

    
    return message


def compose_alerts_for_all(scored_tickets_with_escalation, jira_site, retrieval_data=None):
    """
    Takes the output of escalation.get_escalations_for_all() and returns
    formatted alert strings. If retrieval_data (historical_tickets, embeddings)
    is provided, enriches each alert with similar past tickets.
    """
    from src.retrieval import find_similar_tickets

    messages = []
    for ticket in scored_tickets_with_escalation:
        similar = None
        if retrieval_data and ticket["escalation"]["should_alert"]:
            historical_tickets, embeddings = retrieval_data
            similar = find_similar_tickets(ticket["summary"], historical_tickets, embeddings, top_k=2)

        msg = compose_alert(ticket, ticket["escalation"], jira_site, similar_tickets=similar)
        if msg:
            messages.append(msg)
    return messages


if __name__ == "__main__":
    sample_ticket = {
        "key": "KAN-6",
        "summary": "Login page throwing 500 error",
        "priority": "Highest",
        "pct_of_sla_used": 149.0,
    }
    sample_escalation = {
        "should_alert": True,
        "notify_tier": "L2",
        "message_prefix": "SLA BREACHED",
    }

    msg = compose_alert(sample_ticket, sample_escalation, "https://rishadesai99-sla.atlassian.net")
    print(msg)