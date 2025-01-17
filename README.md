# Gradescope2Google

Automate the process of syncing your Gradescope deadlines to Google Calendar. This script fetches assignment deadlines from Gradescope, creates events in your Google Calendar with custom color codes, and includes functionality to delete these events if needed. Designed for busy students who want to stay on top of deadlines without manually updating their calendars.

## Features
- **Scrapes Gradescope assignments:** Automatically fetches assignment details from Gradescope.
- **Adds deadlines to Google Calendar:** Assignments are added as events with course-specific colors.
- **Deletes events from Google Calendar:** Easily remove events created by the script.
- **Daily automation:** Schedule the script to run daily via crontab for continuous updates.

---

## Prerequisites

### Tools and Accounts Needed:
- Python 3.7+ installed on your system.
- A Google Cloud Project with the Calendar API enabled.
- Access to your Gradescope account.

### Install Required Packages

Clone this repository and navigate to the project directory:
```bash
cd Gradescope2Google
```

Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

---

## Setup

### 1. Google Calendar API Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Google Calendar API** for your project.
4. Go to the **Credentials** tab and create **OAuth 2.0 Client IDs**:
   - Application type: Desktop app.
5. Download the `credentials.json` file and place it in the project directory.
6. Run the script once to generate a `token.json` file:
   ```bash
   python3 main.py
   ```
   Follow the on-screen instructions to authorize the application.

### 2. Gradescope Configuration

1. Rename `example_config.json` to `config.json`:
   ```bash
   mv example_config.json config.json
   ```
2. Open `config.json` and update it with your Gradescope credentials and course IDs:
   ```json
   {
       "username": "your_email@domain.com",
       "password": "your_password",
       "course_ids": ["940384", "933351"]
   }
   ```
   - Replace `course_ids` with the IDs of your Gradescope courses. You can find these in the URL when viewing a course on Gradescope (e.g., `https://www.gradescope.com/courses/940384`).
     
3. Change the color map dictionary to your courses and colors of your choice.

---

## How to Use

### 1. Run the Main Script
To scrape Gradescope deadlines and add them to Google Calendar:
```bash
python3 main.py
```

This will:
- Log in to Gradescope.
- Fetch deadlines and save them in `output/selenium_deadlines.json`.
- Add events to Google Calendar and log them in `output/event_log.json`.

### 2. Delete Events
To delete events created by the script:
```bash
python3 delete_event.py
```

This will read the `event_log.json` file and delete all corresponding events from your Google Calendar.

---

## Automate with Crontab (macOS)

### 1. Open the Crontab Editor
```bash
crontab -e
```

### 2. Schedule the Script
Add the following line to run `main.py` daily at midnight:
```bash
0 0 * * * /path/to/venv/bin/python /path/to/main.py >> /path/to/logs/main.log 2>&1
```
Replace:
- `/path/to/venv/bin/python` with the path to your Python interpreter in the virtual environment.
- `/path/to/main.py` with the path to `main.py`.
- `/path/to/logs/main.log` with the path to a log file for storing output.

Save and exit. Your script will now run daily.

---

## Troubleshooting

### Common Issues
1. **Login failed:**
   - Verify your Gradescope credentials in `config.json`.
   - Ensure Gradescope isn’t requiring additional authentication (e.g., CAPTCHA).

2. **Google Calendar API errors:**
   - Ensure `credentials.json` and `token.json` exist in the project directory.
   - Verify the Google Calendar API is enabled for your Google Cloud project.

3. **Crontab not running:**
   - Ensure the Python virtual environment path in the crontab entry is correct.
   - Check crontab logs: `cat /var/log/syslog` (Linux) or `grep CRON /var/log/system.log` (macOS).

---

## Contributing
Feel free to fork this repository, submit pull requests, or report issues. Contributions are always welcome!

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.



