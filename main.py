import os
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration paths
BASE_DIR = os.path.expanduser("~/Documents/Documents - Aditya’s MacBook Pro/VisualStudioCode/VSC/Gradescope2Google")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEADLINES_FILE = os.path.join(OUTPUT_DIR, "selenium_deadlines.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "event_log.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load configuration
with open(CONFIG_PATH, 'r') as config_file:
    config = json.load(config_file)

def setup_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

def scrape_deadlines():
    LOGIN_URL = "https://www.gradescope.com/login"
    COURSE_NAMES = {"940384": "MAT 111", "933351": "MAT 145"}

    driver = setup_selenium()
    print("Logging in to Gradescope...")

    try:
        driver.get(LOGIN_URL)
        driver.find_element(By.NAME, 'session[email]').send_keys(config['username'])
        driver.find_element(By.NAME, 'session[password]').send_keys(config['password'])
        driver.find_element(By.NAME, 'commit').click()

        if "Invalid email/password combination." in driver.page_source:
            print("Login failed. Please check your credentials.")
            driver.quit()
            return

        print("Login successful!")
        all_assignments = []

        for course_id in config['course_ids']:
            course_name = COURSE_NAMES.get(course_id, "Unknown Course")
            assignments_url = f"https://www.gradescope.com/courses/{course_id}"
            driver.get(assignments_url)

            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "assignments-student-table"))
                )
            except:
                print(f"Timeout waiting for assignments table for course {course_name}")
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.select('#assignments-student-table tbody tr')

            for row in rows:
                title_element = row.select_one('th.table--primaryLink a, th.table--primaryLink button')
                deadline_element = row.select_one('time.submissionTimeChart--dueDate')
                if title_element and deadline_element:
                    all_assignments.append({
                        'course_name': course_name,
                        'name': title_element.text.strip(),
                        'deadline': deadline_element['datetime']
                    })

        with open(DEADLINES_FILE, 'w') as f:
            json.dump(all_assignments, f, indent=4)
        print(f"Deadlines saved to {DEADLINES_FILE}")
    finally:
        driver.quit()

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

def event_exists(service, event_summary, start_time):
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat(),
        timeMax=(start_time + timedelta(hours=1)).isoformat(),
        q=event_summary,
        singleEvents=True
    ).execute()
    events = events_result.get('items', [])
    return any(event['summary'] == event_summary for event in events)

def add_to_calendar():
    with open(DEADLINES_FILE, 'r') as f:
        deadlines = json.load(f)

    service = get_calendar_service()
    log = []

    color_map = {
        "MAT 111": "8",  # Grey
        "MAT 145": "6"   # Orange
    }

    for deadline in deadlines:
        course_name = deadline['course_name']
        event_name = deadline['name']
        event_deadline = deadline['deadline']

        try:
            start_time = datetime.strptime(event_deadline, '%Y-%m-%d %H:%M:%S %z')
        except ValueError:
            print(f"Skipping event due to invalid date format: {event_deadline}")
            continue

        end_time = start_time + timedelta(hours=1)

        if event_exists(service, f"{course_name}: {event_name}", start_time):
            print(f"Duplicate event skipped: {course_name}: {event_name}")
            continue

        event = {
            'summary': f"{course_name}: {event_name}",
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'America/Los_Angeles'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'America/Los_Angeles'},
            'colorId': color_map.get(course_name, "3")  # Default to purple if course not mapped
        }
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event added: {created_event.get('htmlLink')}")
        log.append({
            'course_name': course_name,
            'event_name': event_name,
            'start_time': start_time.isoformat(),
            'event_id': created_event.get('id'),
            'event_link': created_event.get('htmlLink')
        })

    with open(LOG_FILE, 'w') as log_file:
        json.dump(log, log_file, indent=4)
    print(f"Event log saved to {LOG_FILE}")

def main():
    scrape_deadlines()
    add_to_calendar()

if __name__ == "__main__":
    main()
