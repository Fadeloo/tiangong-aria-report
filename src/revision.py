"""Helpers for applying revision directives to generated drafts."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .drafting import Draft

LOGGER = logging.getLogger(__name__)


@dataclass
class RevisionDirectives:
    """Normalized representation of revision instructions."""

    title: str | None
    sections: Dict[str, str]


def parse_revision_file(path: Path) -> RevisionDirectives:
    """Return the desired title override and section replacements from a markdown file.

    The parser expects the following lightweight structure:

    - Optional first-level heading (`# New Title`) to override the draft title.
    - One or more second-level headings (`## Section Name`) followed by replacement text.

    All content under a section heading replaces the corresponding draft section
    verbatim. Sections not present in the directives remain untouched.
    """

    text = path.read_text(encoding="utf-8")
    title: str | None = None
    sections: "OrderedDict[str, str]" = OrderedDict()

    current_section: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if current_section is None:
            return
        sections[current_section] = "\n".join(buffer).strip()

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line and buffer:
            buffer.append("")
            continue
        if line.startswith("# "):
            if title is None and not sections:
                title_candidate = line[2:].strip()
                title = title_candidate if title_candidate else None
                continue
        if line.startswith("## "):
            flush()
            current_section = line[3:].strip()
            buffer = []
            continue
        buffer.append(line)

    flush()
    cleaned_sections = {key: value for key, value in sections.items() if value}
    return RevisionDirectives(title=title, sections=cleaned_sections)


def apply_revision_directives(draft: Draft, directives_path: Path) -> Draft:
    """Return a new draft with revisions applied when directives are present."""

    if not directives_path.exists():
        LOGGER.info("No revision directives found at %s; skipping revision step.", directives_path)
        return draft

    directives = parse_revision_file(directives_path)
    updated_sections: Dict[str, str] = dict(draft.sections)

    for section, replacement in directives.sections.items():
        if not replacement:
            LOGGER.debug("Skipping empty replacement for section '%s'.", section)
            continue
        if section in updated_sections:
            LOGGER.info("Replacing section '%s' based on revision directives.", section)
            updated_sections[section] = replacement
        else:
            LOGGER.warning(
                "Revision directives specify new section '%s' not present in draft; appending.",
                section,
            )
            updated_sections[section] = replacement

    new_title = directives.title or draft.title
    return Draft(title=new_title, sections=updated_sections)
