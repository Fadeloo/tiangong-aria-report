"""Entry point for running the writing pipeline end-to-end."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import run_default


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments."""

    parser = argparse.ArgumentParser(description="Run the tiangong-aria-report pipeline")
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
    return parser.parse_args()


def main() -> None:
    """Execute the configured pipeline."""

    args = parse_args()
    run_default(args.base_path, args.title)


if __name__ == "__main__":
    main()
