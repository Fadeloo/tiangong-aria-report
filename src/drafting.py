"""Draft generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Sequence

from .organization import Segment
from .outline import OutlinePlan, OutlineSection
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


class SectionWriter(Protocol):
    """Contract implemented by orchestration layers that craft section prose."""

    def write_section(self, section: OutlineSection, segments: Sequence[Segment]) -> str:
        """Return fully drafted prose for the supplied outline section."""


def build_draft(
    outline: OutlinePlan,
    segment_lookup: Dict[str, List[Segment]],
    title: str,
    section_writer: Optional[SectionWriter] = None,
) -> Draft:
    """Create a draft by delegating each section to the configured writer."""

    sections: Dict[str, str] = {}
    for section in outline.sections:
        key = section.title.lower().replace(" ", "_")
        bucket_segments = segment_lookup.get(key, [])
        if section_writer is not None:
            generated = section_writer.write_section(section, bucket_segments)
            sections[section.title] = generated or "TODO: Add content"
            continue
        combined = "\n\n".join(segment.text for segment in bucket_segments)
        sections[section.title] = combined or "TODO: Add content"
    return Draft(title=title, sections=sections)


def save_draft(draft: Draft, destination: Path) -> None:
    """Write the draft's text representation to disk."""

    write_text_file(destination, draft.to_text())
