import os
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration paths
BASE_DIR = os.path.expanduser("~/Documents/Documents - Aditya’s MacBook Pro/VisualStudioCode/VSC/Gradescope2Google")
LOG_FILE = os.path.join(BASE_DIR, "output", "event_log.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def delete_events():
    # Load the event log
    if not os.path.exists(LOG_FILE):
        print(f"Log file not found: {LOG_FILE}")
        return

    with open(LOG_FILE, 'r') as log_file:
        events = json.load(log_file)

    if not events:
        print("No events to delete.")
        return

    service = get_calendar_service()

    for event in events:
        try:
            event_id = event.get('event_id')
            if not event_id:
                print(f"Skipping event with missing ID: {event['event_name']} ({event['course_name']})")
                continue

            # Delete the event by ID
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            print(f"Deleted event: {event['event_name']} ({event['course_name']})")
        except Exception as e:
            print(f"Failed to delete event: {event['event_name']} ({event['course_name']}). Error: {e}")

def main():
    delete_events()

if __name__ == "__main__":
    main()
