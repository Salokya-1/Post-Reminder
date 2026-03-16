from __future__ import annotations

from datetime import date
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

from converter import convert_xlsx_to_csv
from run_desktop import CSV_PATH, XLSX_PATH, due_events, ensure_dirs, load_events, seed_csv_if_missing

BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"

app = Flask(__name__)
app.secret_key = "post-reminder-web-secret"


def ensure_web_dirs() -> None:
    ensure_dirs()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/")
def dashboard() -> str:
    today = date.today()
    events = sorted(load_events(), key=lambda item: item.date)
    reminders = due_events(events, today)

    source = "events.csv"
    if XLSX_PATH.exists():
        source = XLSX_PATH.name

    return render_template(
        "dashboard.html",
        today=today,
        total_events=len(events),
        due_reminders=reminders,
        events=events,
        source_file=source,
    )


@app.route("/convert", methods=["GET", "POST"])
def convert() -> str:
    if request.method == "GET":
        return render_template("convert.html")

    file = request.files.get("xlsx_file")
    if file is None or not file.filename:
        flash("Please choose an XLSX file first.", "error")
        return redirect(url_for("convert"))

    if not file.filename.lower().endswith(".xlsx"):
        flash("Only .xlsx files are supported.", "error")
        return redirect(url_for("convert"))

    ensure_web_dirs()
    uploaded_path = UPLOADS_DIR / file.filename
    file.save(uploaded_path)

    try:
        convert_xlsx_to_csv(uploaded_path, CSV_PATH)
        uploaded_path.replace(XLSX_PATH)
    except Exception as exc:
        flash(f"Conversion failed: {exc}", "error")
        return redirect(url_for("convert"))

    flash("Upload successful. Dashboard updated.", "success")
    return redirect(url_for("dashboard"))


ensure_web_dirs()
seed_csv_if_missing()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
