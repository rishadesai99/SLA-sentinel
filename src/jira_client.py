
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SITE = os.getenv("JIRA_SITE")
EMAIL = os.getenv("JIRA_EMAIL")
TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def fetch_open_tickets():
    """
    Fetches all tickets in the project that are not yet resolved.
    Returns a list of raw Jira issue dicts.
    """
    url = f"{SITE}/rest/api/3/search/jql"
    jql = f'project = {PROJECT_KEY} ORDER BY created DESC'
    params = {
        "jql": jql,
        "maxResults": 100,
        "fields": "summary,priority,status,created,resolutiondate,issuetype"
    }

    response = requests.get(url, params=params, auth=(EMAIL, TOKEN))
    response.raise_for_status()
    return response.json()["issues"]


if __name__ == "__main__":
    tickets = fetch_open_tickets()
    print(f"Fetched {len(tickets)} open tickets from project {PROJECT_KEY}\n")
    for t in tickets:
        f = t["fields"]
        priority = f["priority"]["name"] if f["priority"] else "None"
        print(f"{t['key']:<8} | {priority:<8} | {f['status']['name']:<12} | {f['summary']}")
