"""
Reusable HTTP GET with retry logic and exponential backoff.

Every extraction module funnels its requests through fetch_json() so
retry behavior, timeouts, and failure logging are consistent across
all four data sources.
"""

import time

import requests

from src.config import BACKOFF_BASE, MAX_RETRIES, REQUEST_TIMEOUT
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Retry on transient server-side and rate-limit statuses only.
# 4xx client errors (bad variable name, bad key) fail fast because
# retrying them will never succeed.
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class APIError(Exception):
    """Raised when a request fails after all retry attempts."""


def fetch_json(url: str, params: dict | None = None, source: str = "api"):
    """
    GET a URL and return parsed JSON, retrying transient failures.

    Parameters
    ----------
    url : str
        Full endpoint URL.
    params : dict, optional
        Query string parameters.
    source : str
        Short label ("census", "nass", ...) used in log lines.

    Raises
    ------
    APIError
        After MAX_RETRIES failed attempts, or immediately on a
        non-retryable client error.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                return response.json()

            if response.status_code in RETRYABLE_STATUS:
                last_error = f"HTTP {response.status_code}"
                logger.warning(
                    "[%s] attempt %d/%d failed (%s), backing off",
                    source, attempt, MAX_RETRIES, last_error,
                )
            else:
                # Non-retryable: surface the body, it usually explains the problem
                raise APIError(
                    f"[{source}] HTTP {response.status_code}: {response.text[:300]}"
                )

        except requests.exceptions.RequestException as exc:
            last_error = str(exc)
            logger.warning(
                "[%s] attempt %d/%d raised %s",
                source, attempt, MAX_RETRIES, type(exc).__name__,
            )

        if attempt < MAX_RETRIES:
            wait = BACKOFF_BASE ** attempt
            time.sleep(wait)

    raise APIError(f"[{source}] failed after {MAX_RETRIES} attempts: {last_error}")
