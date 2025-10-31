"""Ingestion utilities for collecting raw materials and writing briefs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from .utils import read_text_directory


@dataclass
class WritingBrief:
    """Structured representation of the user's writing request."""

    title: str
    audience: str
    tone: str
    delivery_format: str
    additional_notes: Dict[str, str] = field(default_factory=dict)


@dataclass
class MaterialRecord:
    """A single ingested artifact ready for downstream organization."""

    identifier: str
    content: str
    metadata: Dict[str, str] = field(default_factory=dict)


def load_materials(raw_directory: Path) -> List[MaterialRecord]:
    """Load `.txt` files from the raw materials directory.

    Parameters
    ----------
    raw_directory: Path
        Folder containing user-provided source materials.
    """

    contents = read_text_directory(raw_directory)
    return [MaterialRecord(identifier=name, content=text) for name, text in contents.items()]
