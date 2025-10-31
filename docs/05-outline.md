# 05 Outline

Use this file to capture the approved structure for the deliverable. Each heading and bullet must cite its supporting evidence from `materials/organized/` and align with the objectives documented in `docs/01-project-overview.md`.

## Context

- Processed insights (`docs/04-processed-material-summary.md`)
- Client requirements (`docs/01-project-overview.md`)
- Narrative style guides (`templates/narrative/`)
- Outline utilities (`src/outline.py`)
- Segment inventory (`materials/organized/_index.csv`)

## Available Tools

- `src.outline.generate_outline` to bootstrap section ordering
- Collaborative outlining tools (e.g., Google Docs outline mode) for workshops
- Citation helpers or reference managers to track source identifiers

## Process

1. Import priority insights from `docs/04-processed-material-summary.md`, mapping each to a proposed section.
2. Run `generate_outline` for a draft structure. Paste the resulting sections here as a starting point.
3. Refine section titles, ordering, and bullet depth to reflect client expectations (tone, emphasis, scope).
4. For every bullet, append a parenthetical reference such as `(Segment: background/01)` to maintain traceability.
5. Mark open questions or pending research beneath the affected section with `TODO` callouts.
6. Obtain stakeholder sign-off before transitioning to drafting; record approval date and approver name.

## Output Expectations

- Hierarchical outline with headings, sub-bullets, and source references.
- Clear delineation of optional vs. mandatory components.
- Visible TODOs or risks that must be resolved before drafting begins.
