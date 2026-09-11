import json
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # small, fast, good enough for this use case
_model = None  # loaded lazily, only once


def get_model():
    global _model
    if _model is None:
        print("Loading embedding model (first time only, may take a moment)...")
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_historical_tickets(path="data/resolved_tickets_sample.json"):
    with open(path, "r") as f:
        return json.load(f)


def build_ticket_index(historical_tickets):
    """
    Converts each historical ticket's summary into an embedding vector.
    Returns the tickets list plus a matrix of their embeddings, ready for search.
    """
    model = get_model()
    summaries = [t["summary"] for t in historical_tickets]
    embeddings = model.encode(summaries, convert_to_numpy=True)
    return historical_tickets, embeddings


def find_similar_tickets(query_text, historical_tickets, embeddings, top_k=3):
    """
    Given a new ticket's text, finds the top_k most similar historical tickets
    using cosine similarity between embeddings.
    """
    model = get_model()
    query_embedding = model.encode([query_text], convert_to_numpy=True)[0]

    # Cosine similarity: dot product of normalized vectors
    def cosine_sim(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    scores = [cosine_sim(query_embedding, emb) for emb in embeddings]
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in ranked_indices:
        ticket = historical_tickets[idx]
        results.append({
            "key": ticket["key"],
            "summary": ticket["summary"],
            "resolution": ticket["resolution"],
            "similarity_score": round(float(scores[idx]), 3)
        })
    return results


if __name__ == "__main__":
    historical = load_historical_tickets()
    tickets, embeddings = build_ticket_index(historical)

    test_query = "Login page throwing 500 error"
    print(f"Query: {test_query}\n")

    similar = find_similar_tickets(test_query, tickets, embeddings, top_k=3)
    for s in similar:
        print(f"[{s['similarity_score']}] {s['key']}: {s['summary']}")
        print(f"    Resolution: {s['resolution']}\n")