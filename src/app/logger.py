import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path

CURRENT_FILE_DIR = Path(__file__).resolve().parent
LOG_DIR = CURRENT_FILE_DIR.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = LOG_DIR / "bot.log"

LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s "

logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)

file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10485760, backupCount=5)
file_handler.setLevel(LOGGING_LEVEL)
file_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))

logging.getLogger("").addHandler(file_handler)