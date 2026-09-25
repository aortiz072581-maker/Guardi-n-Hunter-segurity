import logging
from pathlib import Path

from guardian_hunter.config.settings import LOG_DIR

LOG_FILE = LOG_DIR / "guardian_hunter.log"

def setup_logger():
    logger = logging.getLogger("guardian_hunter")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
