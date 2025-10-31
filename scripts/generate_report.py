"""CLI helper to run the pipeline with custom metadata overrides."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from src.pipeline import run_default


def parse_metadata(items: list[str] | None) -> Dict[str, str]:
    """Convert key=value strings into a dictionary."""

    metadata: Dict[str, str] = {}
    if not items:
        return metadata
    for item in items:
        if "=" not in item:
            raise ValueError(f"Metadata entry must be key=value, got: {item}")
        key, value = item.split("=", maxsplit=1)
        metadata[key.strip()] = value.strip()
    return metadata


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments."""

    parser = argparse.ArgumentParser(description="Generate a report with metadata overrides")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve materials and outputs.",
    )
    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Title for the generated draft.",
    )
    parser.add_argument(
        "--meta",
        action="append",
        default=None,
        help="Repeatable key=value metadata overrides appended to the delivery package.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the report generation workflow."""

    args = parse_args()
    overrides = parse_metadata(args.meta)
    run_default(args.base_path, args.title, metadata_overrides=overrides)


if __name__ == "__main__":
    main()
