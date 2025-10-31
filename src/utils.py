"""Utility helpers for filesystem and text handling within tiangong-aria-report."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

LOGGER = logging.getLogger(__name__)


def read_text_directory(directory: Path) -> Dict[str, str]:
    """Return a mapping of relative file names to their UTF-8 text contents.

    Parameters
    ----------
    directory: Path
        Folder containing text files that should be ingested.

    Raises
    ------
    FileNotFoundError
        If the directory does not exist.
    UnicodeDecodeError
        If a file cannot be decoded using UTF-8.
    """

    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")

    contents: Dict[str, str] = {}
    for text_file in directory.rglob("*.txt"):
        LOGGER.debug("Reading text file: %s", text_file)
        contents[str(text_file.relative_to(directory))] = text_file.read_text(encoding="utf-8")
    return contents


def ensure_directory(path: Path) -> Path:
    """Create a directory if it is missing and return the path."""

    path.mkdir(parents=True, exist_ok=True)
    LOGGER.debug("Ensured directory exists: %s", path)
    return path


def write_text_file(destination: Path, text: str) -> None:
    """Persist text to a UTF-8 encoded file, ensuring parent directories exist."""

    ensure_directory(destination.parent)
    destination.write_text(text, encoding="utf-8")
    LOGGER.info("Wrote text output to %s", destination)
