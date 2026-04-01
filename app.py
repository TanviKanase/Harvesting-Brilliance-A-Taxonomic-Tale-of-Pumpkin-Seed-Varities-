from pathlib import Path
import os
import runpy
import threading
import time
import webbrowser


ROOT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ROOT_DIR / "pumpkin-seed"
APP_URL = "http://127.0.0.1:5000"


def open_browser() -> None:
    time.sleep(2)
    try:
        webbrowser.open(APP_URL)
    except Exception:
        pass


def main() -> None:
    if not PROJECT_DIR.exists():
        raise FileNotFoundError(f"Project folder not found: {PROJECT_DIR}")

    os.chdir(PROJECT_DIR)
    print(f"Open {APP_URL} if the browser does not start automatically.")
    threading.Thread(target=open_browser, daemon=True).start()
    runpy.run_path(str(PROJECT_DIR / "app.py"), run_name="__main__")


if __name__ == "__main__":
    main()
