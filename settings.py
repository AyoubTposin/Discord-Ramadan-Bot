import os
import pathlib
from typing import Final
from dotenv import load_dotenv
import logging
from logging.config import dictConfig

load_dotenv()

TOKEN: Final[str]= os.getenv('DISCORD_TOKEN')
BASE_DIR = pathlib.Path(__file__).parent
CMD_DIR = BASE_DIR / "cmds"
COGS_DIR = BASE_DIR / "cogs"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "infos.log")

# Ensure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)
# Ensure the log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        pass  # Creates an empty file

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
dictConfig(LOGGING_CONFIG)