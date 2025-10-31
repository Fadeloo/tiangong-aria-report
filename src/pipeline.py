"""High-level orchestration for the tiangong-aria-report workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .drafting import Draft, build_draft, save_draft
from .export import DeliveryPackage
from .ingestion import load_materials
from .organization import persist_segments, segment_materials
from .outline import generate_outline


@dataclass
class PipelineConfig:
    """Configuration describing filesystem layout for the pipeline."""

    title: str
    raw_dir: Path
    organized_dir: Path
    draft_path: Path
    final_dir: Path


class WritingPipeline:
    """Orchestrate the end-to-end document creation workflow."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

    def run(self, metadata_overrides: Optional[Dict[str, str]] = None) -> DeliveryPackage:
        """Execute the pipeline and return a delivery package."""

        materials = load_materials(self.config.raw_dir)
        segments = segment_materials(materials)
        persist_segments(segments, self.config.organized_dir)

        outline = generate_outline(segments)
        draft = build_draft(outline, segments, self.config.title)
        save_draft(draft, self.config.draft_path)

        metadata: Dict[str, str] = {
            "title": self.config.title,
            "materials_count": str(len(materials)),
            "sections": str(len(draft.sections)),
        }
        if metadata_overrides:
            metadata.update(metadata_overrides)

        package = DeliveryPackage(draft=draft, metadata=metadata)
        package.write(self.config.final_dir)
        return package


def default_config(base_path: Path, title: str) -> PipelineConfig:
    """Construct a PipelineConfig rooted at the given base path."""

    return PipelineConfig(
        title=title,
        raw_dir=base_path / "materials" / "raw",
        organized_dir=base_path / "materials" / "organized",
        draft_path=base_path / "materials" / "output" / "drafts" / "draft.md",
        final_dir=base_path / "materials" / "output" / "final",
    )


def run_default(base_path: Path, title: str, metadata_overrides: Optional[Dict[str, str]] = None) -> DeliveryPackage:
    """Convenience helper to execute the pipeline given a root path and title."""

    pipeline = WritingPipeline(default_config(base_path, title))
    return pipeline.run(metadata_overrides=metadata_overrides)
