from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.intake_triage import triage_tickets
from src.routing import recommend_assignee

from src.jira_client import fetch_open_tickets, SITE
from src.redaction import redact_ticket
from src.risk_engine import load_sla_policy, score_all_tickets
from src.escalation import load_escalation_policy, get_escalations_for_all
from src.dedup import filter_new_alerts
from src.retrieval import load_historical_tickets, build_ticket_index
from src.alert_composer import compose_alerts_for_all
from src.slack_client import send_all_alerts
from src.db import init_db, save_scored_tickets


class AgentState(TypedDict):
    tickets: list
    scored: list
    scored_with_escalation: list
    new_alerts_only: list
    alerts: list
    sent_count: int


def ingest_node(state: AgentState) -> AgentState:
    """Fetches tickets from Jira and redacts PII."""
    tickets = fetch_open_tickets()
    tickets = [redact_ticket(t) for t in tickets]
    state["tickets"] = tickets
    return state


def score_node(state: AgentState) -> AgentState:
    """Scores each ticket's SLA breach risk and saves to the database."""
    init_db()
    policy = load_sla_policy()
    scored = score_all_tickets(state["tickets"], policy)
    save_scored_tickets(scored)
    state["scored"] = scored
    return state

def triage_node(state: AgentState) -> AgentState:
    """Checks each scored ticket for missing context (error codes, steps, etc.)."""
    state["scored"] = triage_tickets(state["scored"])
    return state

def escalate_node(state: AgentState) -> AgentState:
    """Decides who to notify for each ticket, then filters out recently-alerted ones."""
    escalation_policy = load_escalation_policy()
    scored_with_escalation = get_escalations_for_all(state["scored"], escalation_policy)
    state["scored_with_escalation"] = scored_with_escalation
    state["new_alerts_only"] = filter_new_alerts(scored_with_escalation, window_hours=1)
    return state

def alert_node(state: AgentState) -> AgentState:
    """Retrieves similar past tickets, recommends an assignee, composes alerts, sends to Slack."""
    historical_tickets = load_historical_tickets()
    retrieval_data = build_ticket_index(historical_tickets)
    tickets, embeddings = retrieval_data

    for ticket in state["new_alerts_only"]:
        routing = recommend_assignee(ticket["summary"], tickets, embeddings)
        ticket["routing"] = routing

    alerts = compose_alerts_for_all(state["new_alerts_only"], SITE, retrieval_data=retrieval_data)
    state["alerts"] = alerts
    state["sent_count"] = send_all_alerts(alerts)
    return state

def build_graph():
    """Wires the 4 nodes into a single linear agent graph."""
    graph = StateGraph(AgentState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("score", score_node)
    graph.add_node("escalate", escalate_node)
    graph.add_node("alert", alert_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "score")
    graph.add_edge("score", "escalate")
    graph.add_edge("escalate", "alert")
    graph.add_edge("alert", END)

    return graph.compile()


if __name__ == "__main__":
    print("SLA Sentinel Agent — LangGraph Orchestration\n" + "=" * 50)

    app = build_graph()
    result = app.invoke({})

    print(f"\nTickets fetched: {len(result['tickets'])}")
    print(f"Tickets scored: {len(result['scored'])}")
    print(f"New alerts (after dedup): {len(result['new_alerts_only'])}")
    print(f"Alerts composed: {len(result['alerts'])}")
    print(f"Alerts sent to Slack: {result['sent_count']}")