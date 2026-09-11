import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_alert(message):
    """
    Posts a single message to the configured Slack channel via webhook.
    Returns True if it succeeded, False otherwise.
    """
    if not WEBHOOK_URL:
        print("No SLACK_WEBHOOK_URL configured, skipping Slack post.")
        return False

    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        return True
    else:
        print(f"Slack post failed: {response.status_code} - {response.text}")
        return False


def send_all_alerts(alert_messages):
    """Sends a list of alert strings to Slack, one message each."""
    sent_count = 0
    for msg in alert_messages:
        if send_slack_alert(msg):
            sent_count += 1
    return sent_count


if __name__ == "__main__":
    success = send_slack_alert("Test message from SLA Sentinel — if you see this, it works!")
    print("Sent successfully" if success else "Failed to send")