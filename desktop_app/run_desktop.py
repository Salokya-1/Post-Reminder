from __future__ import annotations

import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

from event_loader import Event, load_events_from_csv, load_events_from_xlsx

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "events.csv"
XLSX_PATH = DATA_DIR / "socialmedia_calendar.xlsx"
ROOT_XLSX_PATH = PROJECT_ROOT / "SocialMedia_Calendar_2026.xlsx"
NOTIFIED_STATE = DATA_DIR / "notified_state.json"

try:
    from win10toast import ToastNotifier
except Exception:
    ToastNotifier = None  # type: ignore[assignment]


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def seed_csv_if_missing() -> None:
    if CSV_PATH.exists():
        return

    rows = [
        "name,date,notes",
        "Ugadi,2026-03-20,New year celebration",
        "Ram Navami,2026-03-27,Temple visit",
        "Hanuman Jayanti,2026-04-11,Prayer and offering",
    ]
    CSV_PATH.write_text("\n".join(rows), encoding="utf-8")


def load_events() -> list[Event]:
    if XLSX_PATH.exists():
        events = load_events_from_xlsx(XLSX_PATH)
        if events:
            return events

    if ROOT_XLSX_PATH.exists():
        events = load_events_from_xlsx(ROOT_XLSX_PATH)
        if events:
            return events

    if CSV_PATH.exists():
        return load_events_from_csv(CSV_PATH)

    return []


def due_events(events: list[Event], today: date) -> list[Event]:
    return [event for event in events if event.date - timedelta(days=2) == today]


def load_notified_state() -> dict[str, list[dict[str, str]]]:
    if not NOTIFIED_STATE.exists():
        return {}
    try:
        data = json.loads(NOTIFIED_STATE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_notified_state(state: dict[str, list[dict[str, str]]]) -> None:
    NOTIFIED_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def notify(title: str, message: str) -> None:
    if ToastNotifier is not None:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10, threaded=False)
        return

    print(f"{title}: {message}")


def check_and_notify() -> int:
    today = date.today()
    events = load_events()
    reminders = due_events(events, today)

    if not reminders:
        print("No reminders due today.")
        return 0

    state = load_notified_state()
    day_key = today.isoformat()
    already = {
        (item.get("name", ""), item.get("date", ""))
        for item in state.get(day_key, [])
        if isinstance(item, dict)
    }

    pending = [event for event in reminders if (event.name, event.date.isoformat()) not in already]
    if not pending:
        print("All due reminders were already notified today.")
        return 0

    if len(pending) == 1:
        event = pending[0]
        notify(
            "Post Reminder",
            f"{event.name} is on {event.date.isoformat()} (2-day reminder).",
        )
    else:
        names = ", ".join(event.name for event in pending[:4])
        suffix = "" if len(pending) <= 4 else ", ..."
        notify(
            "Post Reminder",
            f"{len(pending)} events need attention: {names}{suffix}",
        )

    state.setdefault(day_key, [])
    for event in pending:
        state[day_key].append(
            {
                "name": event.name,
                "date": event.date.isoformat(),
                "notes": event.notes,
            }
        )
    save_notified_state(state)

    for event in pending:
        print(f"Notified: {event.name} ({event.date.isoformat()})")
    return len(pending)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Windows reminder notifier")
    parser.add_argument("--once", action="store_true", help="Run one check and exit")
    parser.add_argument(
        "--interval-minutes",
        type=int,
        default=60,
        help="Polling interval in minutes for continuous mode",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    seed_csv_if_missing()

    if args.once:
        check_and_notify()
        return

    print("Post Reminder notifier started. Press Ctrl+C to stop.")
    interval_seconds = max(1, args.interval_minutes) * 60

    while True:
        check_and_notify()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
