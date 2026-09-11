import re

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b')


def redact_text(text):
    """
    Takes a string and masks emails and phone numbers.
    Returns the redacted string.
    """
    if not text:
        return text

    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    return text


def redact_ticket(ticket):
    """
    Takes a raw Jira ticket dict and returns a copy with
    the summary field redacted. Doesn't modify the original.
    """
    fields = ticket["fields"]
    redacted_summary = redact_text(fields.get("summary", ""))

    redacted = dict(ticket)
    redacted["fields"] = dict(fields)
    redacted["fields"]["summary"] = redacted_summary
    return redacted


if __name__ == "__main__":
    sample = {
        "key": "TEST-1",
        "fields": {
            "summary": "User john.doe@example.com couldn't log in, call 9876543210",
        }
    }
    result = redact_ticket(sample)
    print("Before:", sample["fields"]["summary"])
    print("After: ", result["fields"]["summary"])