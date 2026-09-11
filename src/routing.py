from collections import Counter
from src.retrieval import find_similar_tickets


def recommend_assignee(ticket_summary, historical_tickets, embeddings, top_k=3):
    """
    Finds the most similar historical tickets and recommends whoever
    resolved the most of them — a simple 'who's handled this before' heuristic.
    """
    similar = find_similar_tickets(ticket_summary, historical_tickets, embeddings, top_k=top_k)

    resolvers = [
        next(t["resolved_by"] for t in historical_tickets if t["key"] == s["key"])
        for s in similar
    ]

    if not resolvers:
        return {"recommended_assignee": None, "confidence": 0, "based_on": []}

    top_resolver, count = Counter(resolvers).most_common(1)[0]
    confidence = round(count / len(resolvers) * 100, 1)

    return {
        "recommended_assignee": top_resolver,
        "confidence": confidence,
        "based_on": [s["key"] for s in similar],
    }


if __name__ == "__main__":
    from src.retrieval import load_historical_tickets, build_ticket_index

    historical = load_historical_tickets()
    tickets, embeddings = build_ticket_index(historical)

    test_query = "Login page throwing 500 error"
    result = recommend_assignee(test_query, tickets, embeddings)

    print(f"Query: {test_query}")
    print(f"Recommended assignee: {result['recommended_assignee']} (confidence: {result['confidence']}%)")
    print(f"Based on similar tickets: {result['based_on']}")