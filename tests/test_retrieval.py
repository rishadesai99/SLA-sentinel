import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.retrieval import load_historical_tickets, build_ticket_index, find_similar_tickets


def test_historical_tickets_load():
    tickets = load_historical_tickets()
    assert len(tickets) > 0
    assert "summary" in tickets[0]
    assert "resolution" in tickets[0]


def test_similar_ticket_retrieval_finds_relevant_match():
    tickets = load_historical_tickets()
    tickets, embeddings = build_ticket_index(tickets)

    results = find_similar_tickets("Login page throwing 500 error", tickets, embeddings, top_k=1)

    assert len(results) == 1
    assert results[0]["key"] == "HIST-101"  # the most obviously similar one
    assert results[0]["similarity_score"] > 0.5