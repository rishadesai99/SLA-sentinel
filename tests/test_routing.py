import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.routing import recommend_assignee
from src.retrieval import load_historical_tickets, build_ticket_index


def test_recommends_correct_assignee_for_login_issue():
    historical = load_historical_tickets()
    tickets, embeddings = build_ticket_index(historical)

    result = recommend_assignee("Login page throwing 500 error", tickets, embeddings)

    assert result["recommended_assignee"] == "Priya"
    assert result["confidence"] > 0
    assert len(result["based_on"]) > 0