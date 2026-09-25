from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]

LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

APP_NAME = os.getenv("APP_NAME", "Guardian Hunter")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
