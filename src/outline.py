"""Utilities to shape organized insights into a document outline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .organization import Segment


@dataclass
class OutlineSection:
    """Description of a single outline section."""

    title: str
    bullet_points: List[str]


@dataclass
class OutlinePlan:
    """Ordered outline produced from organized material segments."""

    sections: List[OutlineSection]


def _title_from_bucket(bucket_name: str) -> str:
    """Convert an internal bucket key into a human-readable title."""

    words = bucket_name.split("_")
    return " ".join(word.capitalize() for word in words)


def generate_outline(segments: Dict[str, List[Segment]]) -> OutlinePlan:
    """Build a skeleton outline from material segments.

    Parameters
    ----------
    segments:
        Mapping produced by `organization.segment_materials`.
    """

    sections: List[OutlineSection] = []
    for bucket_name, bucket_segments in segments.items():
        if bucket_name == "misc":
            continue
        title = _title_from_bucket(bucket_name)
        bullets: List[str] = []
        for segment in bucket_segments:
            snippet = segment.text.split("。")[0].split(".")[0].strip()
            if not snippet:
                continue
            bullets.append(f"{snippet} ({segment.identifier})")
            if len(bullets) == 5:
                break
        sections.append(OutlineSection(title=title, bullet_points=bullets))
    return OutlinePlan(sections=sections)
