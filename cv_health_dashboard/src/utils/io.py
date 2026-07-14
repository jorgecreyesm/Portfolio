"""Shared file-discovery helpers for the transform and load stages."""

from pathlib import Path


def latest_file(directory: Path, prefix: str) -> Path:
    """Return the most recently modified file in `directory` starting with `prefix`."""
    matches = sorted(directory.glob(f"{prefix}*"), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"No file matching '{prefix}*' found in {directory}")
    return matches[-1]
