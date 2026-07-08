#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from datetime import datetime


# ============================================================
# DIRECTORIOS
# ============================================================
LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)


# ============================================================
# LOGGING
# ============================================================
LOG_FILE = os.path.join(LOGS_DIR, "bot.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

_logger = logging.getLogger('krishna')


def log_info(msg: str) -> None:
    _logger.info(msg)


def log_warning(msg: str) -> None:
    _logger.warning(msg)


def log_error(msg: str) -> None:
    _logger.error(msg)


def log_debug(msg: str) -> None:
    _logger.debug(msg)


def log_success(msg: str) -> None:
    _logger.info(f"✅ {msg}")


# ============================================================
# HELPERS
# ============================================================
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def now():
    return time.time()


def datetime_now():
    return datetime.now().isoformat()
