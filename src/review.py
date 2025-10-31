"""Review utilities to track feedback cycles."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .utils import write_text_file


@dataclass
class ReviewComment:
    """Feedback item captured during a review cycle."""

    author: str
    message: str
    severity: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def format_markdown(self) -> str:
        """Render the comment as a markdown bullet."""

        ts = self.timestamp.isoformat(timespec="seconds")
        return f"- **{self.severity}** | {self.author} | {ts}: {self.message}"


def export_review_notes(comments: Iterable[ReviewComment], destination: Path) -> None:
    """Persist review notes so they can be attached to the documentation trail."""

    lines: List[str] = ["# Review Notes", ""]
    lines.extend(comment.format_markdown() for comment in comments)
    write_text_file(destination, "\n".join(lines))
