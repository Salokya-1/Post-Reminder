from __future__ import annotations

import threading
import time
import webbrowser

from app import app, ensure_dirs, seed_csv_if_missing


def _open_browser() -> None:
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")


def main() -> None:
    ensure_dirs()
    seed_csv_if_missing()

    thread = threading.Thread(target=_open_browser, daemon=True)
    thread.start()

    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
