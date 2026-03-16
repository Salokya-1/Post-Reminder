from __future__ import annotations

import csv
from pathlib import Path

from event_loader import load_events_from_xlsx


def convert_xlsx_to_csv(input_xlsx: Path, output_csv: Path) -> Path:
    events = load_events_from_xlsx(input_xlsx)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "date", "notes"])
        for event in events:
            writer.writerow([event.name, event.date.isoformat(), event.notes])

    return output_csv
