# SLA Sentinel

Agentic AI for support operations — predictive SLA breach detection, contextual
alerts, and assignee routing for a Jira-based support queue. Read-only against
Jira; no auto-actions, no ticket writes, human-in-the-loop by design.

**Status: Phases 0–3 of the original proposal complete and tested.**

---

## What this does

Watches the open ticket queue, predicts which tickets are at risk of breaching
their SLA, retrieves how similar tickets were resolved before, recommends who
should take it, and sends a single enriched alert to Slack — all before a
human has to notice anything is wrong.

## Pipeline

```
Jira Cloud → Ingest & redact → Score & triage → Retrieve & route → Escalate & alert → Slack
```

Orchestrated as a LangGraph agent (`src/agent_graph.py`), not a linear script —
each stage is an independent, connected node.

## What's built and working

### Phase 0 — Data foundation
- Live, read-only ingestion from Jira Cloud REST API (`src/jira_client.py`)
- PII redaction layer — strips emails/phone numbers before any further
  processing, fully unit-tested (`src/redaction.py`)
- Deterministic SLA breach-risk scoring, config-driven via YAML
  (`src/risk_engine.py`, `config/sla_policy.yaml`)
- Persistent storage of every run's scores (`src/db.py`, SQLite)
- Baseline metrics report — real breach-rate numbers computed from ticket
  history (`scripts/baseline_metrics.py`)
- Exploratory analysis notebook with breach distribution charts
  (`notebooks/exploratory_analysis.ipynb`)

### Phase 1 — Deterministic engine + alerts
- Tiered escalation config — who gets notified at what risk level
  (`src/escalation.py`, `config/escalation_policy.yaml`)
- Deduplication and throttling — no repeat alerts on the same ticket within a
  time window (`src/dedup.py`)
- Real Slack delivery via webhook (`src/slack_client.py`)
- Alert usefulness feedback/rating capture (`src/feedback.py`)

### Phase 2 — Retrieval layer (RAG)
- Sentence-embedding-based semantic search over historical resolved tickets
  (`src/retrieval.py`, using `sentence-transformers`)
- Every alert enriched with the most similar past tickets and how they were
  resolved
- Historical sample dataset (`data/resolved_tickets_sample.json`) standing in
  for real resolved-ticket history, not yet available

### Phase 3 — Agent orchestration
- Full pipeline rebuilt as a LangGraph state machine (`src/agent_graph.py`)
- Intake triage node — flags tickets missing required context: error codes,
  steps to reproduce, environment, timestamps (`src/intake_triage.py`)
- Routing recommendation node — suggests a specific assignee based on who
  resolved similar tickets before, with a confidence score (`src/routing.py`)

## Not yet built (by design, scoped for later)

- Phase 4: ML-based predictive risk model, recurring-incident clustering
- Phase 5: hardening, live pilot, cost/latency dashboards, full CI eval suite
- Hybrid (keyword + vector) retrieval — currently pure vector similarity
- PostgreSQL — currently SQLite, functionally equivalent at this scale

## How to run

```bash
pip install -r requirements.txt
python -m src.agent_graph
```

This fetches open Jira tickets, redacts PII, scores SLA risk, triages for
missing context, retrieves similar past resolutions, recommends an assignee,
and posts enriched alerts to Slack — end to end, in one command.

To see just the scoring pipeline without the full agent:
```bash
python scripts/run_ingestion.py
```

To see baseline metrics:
```bash
python scripts/baseline_metrics.py
```

## Configuration

All thresholds and policy live in editable config files, not hardcoded:
- `config/sla_policy.yaml` — SLA hours allowed per priority level
- `config/escalation_policy.yaml` — who gets notified at what risk level,
  alert volume limits

Secrets (Jira credentials, Slack webhook) live in `.env` (never committed —
see `.env.example` for the required keys).

## Tests

```bash
pytest
```

26 automated tests across 10 files, covering redaction, risk scoring,
escalation, deduplication, retrieval, routing, alert composition, feedback,
and the agent graph itself.

## Project structure

```
sla-sentinel/
├── config/                  # SLA policy, escalation policy (YAML)
├── data/                    # Sample historical resolved-ticket dataset
├── notebooks/                # Exploratory analysis
├── scripts/                  # Entrypoints (ingestion, baseline metrics)
├── src/
│   ├── jira_client.py        # Jira API — the only file that talks to Jira
│   ├── redaction.py           # PII stripping
│   ├── risk_engine.py         # SLA breach scoring
│   ├── intake_triage.py       # Missing-context detection
│   ├── escalation.py          # Notification tier decisions
│   ├── dedup.py                # Alert deduplication/throttling
│   ├── retrieval.py            # Embeddings + similarity search (RAG)
│   ├── routing.py              # Assignee recommendation
│   ├── alert_composer.py       # Builds the final alert message
│   ├── slack_client.py         # Slack webhook delivery
│   ├── feedback.py             # Alert usefulness ratings
│   ├── db.py                   # SQLite persistence
│   └── agent_graph.py          # LangGraph orchestration of everything above
└── tests/                     # 26 tests, one file per component
```

## Known engineering notes

- Jira deprecated the original `/search` REST endpoint mid-project; ingestion
  now uses `/search/jql`.
- Retrieval uses a small local embedding model (`all-MiniLM-L6-v2`) — no
  external API calls, no per-query cost.
- Historical ticket data is a representative sample, not real production
  data, since real resolved-ticket history isn't available yet. The
  retrieval and routing logic is unchanged whichever dataset it points at.