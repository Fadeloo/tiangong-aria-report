"""Draft generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .outline import OutlinePlan
from .utils import write_text_file


@dataclass
class Draft:
    """Representation of a generated draft."""

    title: str
    sections: Dict[str, str]

    def to_text(self) -> str:
        """Render the draft into a single markdown string."""

        lines: List[str] = [f"# {self.title}"]
        for heading, content in self.sections.items():
            lines.append(f"\n## {heading}\n")
            lines.append(content)
        return "\n".join(lines)


def build_draft(outline: OutlinePlan, segment_lookup: Dict[str, List[str]], title: str) -> Draft:
    """Create a draft by stitching outline headings to supporting paragraphs."""

    sections: Dict[str, str] = {}
    for section in outline.sections:
        combined = "\n\n".join(segment_lookup.get(section.title.lower(), []))
        sections[section.title] = combined or "TODO: Add content"
    return Draft(title=title, sections=sections)


def save_draft(draft: Draft, destination: Path) -> None:
    """Write the draft's text representation to disk."""

    write_text_file(destination, draft.to_text())
