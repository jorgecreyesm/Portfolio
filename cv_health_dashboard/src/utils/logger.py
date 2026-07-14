"""
Shared logging configuration.

Every module calls get_logger(__name__) so all pipeline output lands in
one timestamped log file per run, plus the console. Data quality flags
are logged at WARNING so they are easy to grep out of a run log.
"""

import logging
import sys
from datetime import datetime

from src.config import LOG_DIR

_RUN_STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
_LOG_FILE = LOG_DIR / f"pipeline_{_RUN_STAMP}.log"
_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger wired to the shared run log file and console."""
    _configure_root()
    return logging.getLogger(name)


def current_log_file() -> str:
    """Path of this run's log file, for inclusion in the run report."""
    return str(_LOG_FILE)
