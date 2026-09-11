import re

# Keywords/patterns that suggest each required piece of context is present
CONTEXT_CHECKS = {
    "error_code": re.compile(r'\b(error|err)[\s:#-]*\d{2,5}\b|\b\d{3}\b.*(error|status)', re.IGNORECASE),
    "steps_to_reproduce": re.compile(r'\b(steps to reproduce|when i|after i|reproduce|repro)\b', re.IGNORECASE),
    "environment": re.compile(r'\b(prod|production|staging|dev|environment|browser|chrome|firefox|safari|mobile|ios|android)\b', re.IGNORECASE),
    "timestamp": re.compile(r'\b(\d{1,2}:\d{2}|am|pm|today|yesterday|since)\b', re.IGNORECASE),
}


def check_ticket_completeness(ticket_summary):
    """
    Scans a ticket's summary text for required context fields.
    Returns a dict showing which fields were found vs missing.
    """
    found = {}
    for field_name, pattern in CONTEXT_CHECKS.items():
        found[field_name] = bool(pattern.search(ticket_summary))

    missing = [field for field, present in found.items() if not present]

    return {
        "found": found,
        "missing_fields": missing,
        "is_complete": len(missing) == 0,
    }


def triage_tickets(scored_tickets):
    """
    Runs completeness check on a list of scored tickets.
    Returns the same tickets with a 'triage' field added to each.
    """
    result = []
    for ticket in scored_tickets:
        triage = check_ticket_completeness(ticket["summary"])
        result.append({**ticket, "triage": triage})
    return result


if __name__ == "__main__":
    samples = [
        {"key": "T-1", "summary": "Login page throwing 500 error"},
        {"key": "T-2", "summary": "Users report app crashes when opening profile on iOS, error 4042, happens since yesterday 3pm"},
    ]

    for s in samples:
        result = check_ticket_completeness(s["summary"])
        print(f"{s['key']}: {s['summary']}")
        print(f"  Complete: {result['is_complete']}")
        print(f"  Missing: {result['missing_fields']}\n")