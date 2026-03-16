from __future__ import annotations

import csv
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

from flask import Flask, flash, redirect, render_template, request, url_for

from converter import convert_xlsx_to_csv
from event_loader import Event, load_events_from_csv, load_events_from_xlsx

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CSV_PATH = DATA_DIR / "events.csv"
XLSX_PATH = DATA_DIR / "socialmedia_calendar.xlsx"
ROOT_XLSX_PATH = PROJECT_ROOT / "SocialMedia_Calendar_2026.xlsx"

app = Flask(__name__)
app.secret_key = "post-reminder-desktop-secret"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def seed_csv_if_missing() -> None:
    if CSV_PATH.exists():
        return

    rows = [
        ["name", "date", "notes"],
        ["Ugadi", "2026-03-20", "New year celebration"],
        ["Ram Navami", "2026-03-27", "Temple visit"],
        ["Hanuman Jayanti", "2026-04-11", "Prayer and offering"],
    ]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def load_events() -> list[Event]:
    if XLSX_PATH.exists():
        return load_events_from_xlsx(XLSX_PATH)

    if ROOT_XLSX_PATH.exists():
        return load_events_from_xlsx(ROOT_XLSX_PATH)

    if CSV_PATH.exists():
        return load_events_from_csv(CSV_PATH)

    return []


def find_due_reminders(events: Iterable[Event], today: date) -> list[Event]:
    due: list[Event] = []
    for event in events:
        if event.date - timedelta(days=2) == today:
            due.append(event)
    return due


@app.route("/")
def dashboard() -> str:
    today = date.today()
    events = sorted(load_events(), key=lambda item: item.date)
    due_reminders = find_due_reminders(events, today)

    return render_template(
        "dashboard.html",
        today=today,
        total_events=len(events),
        due_reminders=due_reminders,
        events=events,
        source_file=(
            XLSX_PATH.name
            if XLSX_PATH.exists()
            else (ROOT_XLSX_PATH.name if ROOT_XLSX_PATH.exists() else CSV_PATH.name)
        ),
    )


@app.route("/convert", methods=["GET", "POST"])
def convert() -> str:
    if request.method == "GET":
        return render_template("convert.html")

    file = request.files.get("xlsx_file")
    if file is None or file.filename is None or file.filename.strip() == "":
        flash("Please choose an XLSX file first.", "error")
        return redirect(url_for("convert"))

    if not file.filename.lower().endswith(".xlsx"):
        flash("Only .xlsx files are supported.", "error")
        return redirect(url_for("convert"))

    ensure_dirs()
    target_upload = UPLOADS_DIR / file.filename
    file.save(target_upload)

    try:
        convert_xlsx_to_csv(target_upload, CSV_PATH)
        # Keep a canonical workbook name as dashboard data source.
        target_upload.replace(XLSX_PATH)
    except Exception as exc:  # pragma: no cover
        flash(f"Conversion failed: {exc}", "error")
        return redirect(url_for("convert"))

    flash("Conversion complete. Dashboard updated.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    ensure_dirs()
    seed_csv_if_missing()
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
