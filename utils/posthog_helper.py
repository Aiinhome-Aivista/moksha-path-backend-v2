import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
POSTHOG_URL = os.getenv("POSTHOG_URL")

def send_event_to_posthog(user_id, event_name, event_data):
    try:
        payload = {
            "api_key": POSTHOG_API_KEY,
            "event": event_name,
            "distinct_id": str(user_id),
            "properties": event_data or {}
        }

        requests.post(POSTHOG_URL, json=payload, timeout=2)

    except Exception as e:
        print("PostHog error:", e)