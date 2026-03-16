# Post Reminder (Android)

Android app to remind festival dates **2 days before** the festival day.

## What this app does

- Reads festivals from your uploaded Excel: `SocialMedia_Calendar_2026.xlsx`
- Uses CSV fallback from `app/src/main/assets/festivals.csv` if Excel is missing
- Shows all festivals in a simple list
- Schedules a daily background check using WorkManager
- Sends a notification when today is `festival_date - 2 days`

## Excel support

The project now uses your uploaded file directly:

- `SocialMedia_Calendar_2026.xlsx` (root of repository)

Expected columns (header names can vary, parser is flexible):

| name | date | notes |
|------|------|-------|
| Ugadi | 2026-03-20 | New year celebration |

Important:

- Date formats supported include `YYYY-MM-DD`, `DD-MM-YYYY`, and month name styles

## How to use your uploaded social media calendar

1. Keep `SocialMedia_Calendar_2026.xlsx` in project root.
2. Rebuild app.
3. Gradle copies the Excel file into app assets automatically.
4. Run app and grant notification permission.

## Build and run

1. Open project in Android Studio.
2. Let Gradle sync finish.
3. Run app on Android device/emulator.
4. Allow notification permission when asked.

## Main files

- `app/src/main/java/com/salokya/postreminder/MainActivity.kt`
- `app/src/main/java/com/salokya/postreminder/FestivalRepository.kt`
- `app/src/main/java/com/salokya/postreminder/FestivalReminderWorker.kt`
- `app/src/main/java/com/salokya/postreminder/ReminderScheduler.kt`
- `app/src/main/assets/festivals.csv`
- `SocialMedia_Calendar_2026.xlsx`

---

# Desktop App (Web Dashboard + XLSX to CSV)

A new desktop version is included in `desktop_app/`.

## Features

- Local web dashboard for events and reminders
- Shows reminders due today (2 days before event date)
- XLSX to CSV converter page
- Reads from `desktop_app/data/socialmedia_calendar.xlsx` first
- Falls back to root `SocialMedia_Calendar_2026.xlsx`
- Falls back to `desktop_app/data/events.csv` if needed

## Run Desktop App

1. Open terminal in `desktop_app`.
2. Install requirements:
   - `python -m pip install -r requirements-web.txt`
3. Start app:
   - `python run_desktop.py`
4. Browser opens at `http://127.0.0.1:5000`.

## Build Windows EXE

From a Windows machine:

1. Open terminal in `desktop_app`.
2. Run:
   - `build_windows_exe.bat`
3. Output EXE:
   - `desktop_app/dist/PostReminderDesktop.exe`

Note:

- `requirements-web.txt` is for web/runtime deploys (Render, Linux CI).
- `requirements.txt` includes `pyinstaller` for Windows EXE packaging.

## Desktop Main Files

- `desktop_app/app.py`
- `desktop_app/event_loader.py`
- `desktop_app/converter.py`
- `desktop_app/run_desktop.py`
- `desktop_app/build_windows_exe.bat`
- `desktop_app/templates/dashboard.html`
- `desktop_app/templates/convert.html`
