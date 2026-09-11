import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent_graph import build_graph


def test_graph_compiles_without_error():
    app = build_graph()
    assert app is not None


def test_graph_has_expected_nodes():
    app = build_graph()
    node_names = set(app.get_graph().nodes.keys())
    expected = {"ingest", "score", "escalate", "alert"}
    assert expected.issubset(node_names)