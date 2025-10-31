"""Export helpers for final deliverables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from .drafting import Draft
from .utils import write_text_file


@dataclass
class DeliveryPackage:
    """Container for the final document and supporting metadata."""

    draft: Draft
    metadata: Dict[str, str]

    def write(self, destination: Path) -> None:
        """Persist the package to the destination folder."""

        markdown_path = destination / "deliverable.md"
        write_text_file(markdown_path, self.draft.to_text())

        metadata_path = destination / "metadata.json"
        write_text_file(metadata_path, json.dumps(self.metadata, indent=2))
