"""Utilities to shape organized insights into a document outline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class OutlineSection:
    """Description of a single outline section."""

    title: str
    bullet_points: List[str]


@dataclass
class OutlinePlan:
    """Ordered outline produced from organized material segments."""

    sections: List[OutlineSection]


def generate_outline(segments: Dict[str, List[str]]) -> OutlinePlan:
    """Build a skeleton outline from material segments.

    Parameters
    ----------
    segments:
        Mapping produced by `organization.segment_materials`.
    """

    sections: List[OutlineSection] = []
    for bucket_name, paragraphs in segments.items():
        title = bucket_name.capitalize()
        bullets = [paragraph.split(". ")[0] for paragraph in paragraphs if paragraph]
        sections.append(OutlineSection(title=title, bullet_points=bullets[:5]))
    return OutlinePlan(sections=sections)
