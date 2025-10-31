"""Logic for organizing ingested materials into structured segments."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

from .ingestion import MaterialRecord
from .utils import write_text_file


def segment_materials(materials: Iterable[MaterialRecord]) -> Dict[str, List[str]]:
    """Group material paragraphs by simple keyword heuristics.

    Segmentation here is intentionally naive and should be replaced with
    project-specific logic. Each paragraph is classified into a bucket based on
    the first keyword match; unmatched paragraphs fall back to the "misc" bucket.

    Returns
    -------
    dict
        Mapping of bucket names to lists of paragraph strings.
    """

    buckets: Dict[str, List[str]] = defaultdict(list)
    keyword_map = {
        "background": ["history", "background", "context"],
        "requirements": ["must", "should", "require"],
        "analysis": ["analysis", "finding", "insight"],
    }

    for record in materials:
        for paragraph in record.content.split("\n\n"):
            normalized = paragraph.lower()
            bucket = "misc"
            for candidate, keywords in keyword_map.items():
                if any(keyword in normalized for keyword in keywords):
                    bucket = candidate
                    break
            buckets[bucket].append(paragraph.strip())
    return buckets


def persist_segments(segments: Dict[str, List[str]], destination: Path) -> None:
    """Write organized segments to disk for inspection."""

    for bucket, paragraphs in segments.items():
        write_text_file(destination / f"{bucket}.txt", "\n\n".join(paragraphs))
