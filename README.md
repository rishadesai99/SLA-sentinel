# SLA Sentinel — Phase 0

Predictive SLA breach detection for the support ticket queue. Read-only, no auto-actions.

## What's working right now
- Live ingestion from Jira Cloud (`src/jira_client.py`)
- Deterministic breach-risk scoring against a configurable SLA policy (`src/risk_engine.py`)
- Ranked risk report via `scripts/run_ingestion.py`

## How to run