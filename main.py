from __future__ import annotations

import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENDOR_DIR = BASE_DIR / "vendor"

if VENDOR_DIR.exists():
    vendor_path = str(VENDOR_DIR)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)

from PyQt6.QtGui import QIcon
from novel_app.ai_service import SimpleAIService
from novel_app.database import Database

APP_ICON = BASE_DIR / "packaging" / "app_icon.ico"


def main() -> None:
    database = Database()
    database.initialize()

    ai_service = SimpleAIService.from_env()
    if os.environ.get("SIMPLE_AI_NOVEL_SMOKE_EXIT") == "1":
        database.close()
        return

    from novel_app.qt_app import run_qt_app

    try:
        raise SystemExit(run_qt_app(database=database, ai_service=ai_service))
    finally:
        database.close()


if __name__ == "__main__":
    main()
