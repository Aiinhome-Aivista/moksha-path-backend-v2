import requests

POSTHOG_API_KEY = "phc_QTG3Kz6La1BL28536wugnIF3XduwvYNh6pVuhGUZN0F"
POSTHOG_URL = "https://app.posthog.com/capture/"

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