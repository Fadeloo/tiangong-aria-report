# 04 Processed Material Summary

This document consolidates insights extracted from `materials/organized/`. Use it as the definitive bridge between raw evidence and the evolving outline. Every summary entry must cite its originating segment identifier and capture validation status.

## Context

- Organized segments (`materials/organized/_index.csv`, `materials/organized/{topic}/`)
- Normalization notes (`docs/02-material-intake.md`)
- Organization rationale (`docs/03-organization-plan.md`)
- Supporting scripts (`src/organization.py`, `src/utils.py`)

## Available Tools

- Spreadsheet filters or pandas notebooks to pivot `_index.csv`
- `uv run python -c "..."` snippets leveraging `segment_materials` output
- Rapid annotation utilities (e.g., Obsidian, Notion) for temporary clustering summaries

## Process

1. Review `_index.csv` and select high-priority segments for synthesis; tag them with `summary_needed = yes` in a working column.
2. Draft bullet-point summaries grouped by topic. For each bullet, include:
   - `Segment ID`
   - `Key Insight`
   - `Source File`
   - `Confidence` (`high`, `medium`, `low`)
3. Capture verification needs in a `Follow-up` column. Flag items requiring corroboration or client confirmation.
4. Maintain a running "Gap Log" section for missing data or conflicting evidence so the outline stage can address them explicitly.
5. Update this document whenever new segments are added or insights change; note the modification date and responsible contributor.

## Output Expectations

- Clear traceability: every summary item links back to `materials/organized/` entries.
- Prioritized list of insights, grouped by topic relevance.
- Explicit confidence and follow-up markers to guide outlining and drafting decisions.
