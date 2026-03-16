# Post Reminder (Windows Notifier)

This repository now focuses on a Windows desktop reminder application.

## What It Does

- Reads events from `SocialMedia_Calendar_2026.xlsx` (root) or `desktop_app/data/socialmedia_calendar.xlsx`
- Falls back to `desktop_app/data/events.csv` if XLSX data is not available
- Sends Windows toast notifications when an event is **2 days away**
- Avoids duplicate notifications on the same day using local state

## Run Locally (Python)

1. Open terminal in `desktop_app`.
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
3. Run continuously (checks every 60 minutes):
   - `python run_desktop.py`
4. Run once (test mode):
   - `python run_desktop.py --once`

## Build Windows EXE

From a Windows machine:

1. Open terminal in `desktop_app`.
2. Run:
   - `build_windows_exe.bat`
3. Output:
   - `desktop_app/dist/PostReminderDesktop.exe`

## Key Files

- `desktop_app/run_desktop.py`
- `desktop_app/event_loader.py`
- `desktop_app/build_windows_exe.bat`
- `desktop_app/requirements.txt`
