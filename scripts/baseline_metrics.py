import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import get_connection


def compute_baseline_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    # Total tickets tracked
    cursor.execute("SELECT COUNT(DISTINCT ticket_key) FROM ticket_scores")
    total_tickets = cursor.fetchone()[0]

    # Breach rate: % of tickets that have EVER been marked BREACHED
    cursor.execute("SELECT COUNT(DISTINCT ticket_key) FROM ticket_scores WHERE status = 'BREACHED'")
    breached_tickets = cursor.fetchone()[0]

    # Breach rate specifically for high-priority tickets (P1/P2 equivalent: Highest/High)
    cursor.execute("""
        SELECT COUNT(DISTINCT ticket_key) FROM ticket_scores
        WHERE status = 'BREACHED' AND priority IN ('Highest', 'High')
    """)
    high_priority_breached = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT ticket_key) FROM ticket_scores WHERE priority IN ('Highest', 'High')")
    high_priority_total = cursor.fetchone()[0]

    # Average elapsed hours across all tracked tickets (proxy for time-to-resolution, since none are resolved yet)
    cursor.execute("SELECT AVG(elapsed_hrs) FROM ticket_scores")
    avg_elapsed = cursor.fetchone()[0]

    conn.close()

    breach_rate = (breached_tickets / total_tickets * 100) if total_tickets else 0
    p1_p2_breach_rate = (high_priority_breached / high_priority_total * 100) if high_priority_total else 0

    return {
        "total_tickets_tracked": total_tickets,
        "overall_breach_rate_pct": round(breach_rate, 1),
        "p1_p2_breach_rate_pct": round(p1_p2_breach_rate, 1),
        "avg_elapsed_hours": round(avg_elapsed, 1) if avg_elapsed else 0,
    }


def print_report(metrics):
    print("SLA Sentinel — Phase 0 Baseline Metrics Report")
    print("=" * 50)
    print(f"Total tickets tracked:         {metrics['total_tickets_tracked']}")
    print(f"Overall breach rate:           {metrics['overall_breach_rate_pct']}%")
    print(f"P1/P2 (Highest/High) breach rate: {metrics['p1_p2_breach_rate_pct']}%")
    print(f"Average ticket age (hours):    {metrics['avg_elapsed_hours']}")
    print("=" * 50)
    print("\nNote: mean time to resolution, escalation rate, and reassignment")
    print("metrics require RESOLVED ticket history, which this sandbox doesn't")
    print("have yet (all sample tickets are still open). These will populate")
    print("once real historical Jira data is ingested.")


if __name__ == "__main__":
    metrics = compute_baseline_metrics()
    print_report(metrics)