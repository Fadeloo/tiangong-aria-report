# 10 Quality Assurance Checklist

Track all validation steps required before final delivery. Update statuses as checks are completed and capture any remediation actions.

## Context

- Drafts in `materials/output/drafts/` and final package in `materials/output/final/`
- Review feedback (`docs/08-review-notes/`)
- Composition timeline (`docs/07-composition-log.md`)
- Client requirements (`docs/01-project-overview.md`) and narrative guides (`templates/narrative/`)
- Tooling outputs (mypy, ruff, fact-check scripts)

## Available Tools

- Automated linters: `uv run mypy src/`, `uv run ruff check src/`, `uv run ruff format --check src/`
- Fact-check spreadsheets or knowledge bases
- Accessibility and formatting validators (e.g., Markdownlint, screen reader previews)
- Style and grammar checkers with exportable reports

## Checklist Template

| Task | Description | Responsible | Status | Evidence/Link | Follow-up |
|------|-------------|-------------|--------|---------------|-----------|
| ex: Factual verification | Cross-verify statistics vs. source segments | Name | pending | link-to-notes | Need client confirmation on 2022 data |

## Process

1. Initialize the checklist with mandatory QA tasks covering content accuracy, tone, formatting, accessibility, and compliance.
2. Assign owners and due dates; update the `Status` column (`pending`, `in-progress`, `blocked`, `complete`).
3. Attach evidence for each completed task (e.g., screenshot, report link, commit hash).
4. Verify that all required revisions from `materials/output/logs/revision-directives.md` have been applied and note residual directives if any.
5. Log any discovered issues in the `Follow-up` column and reference them in `docs/07-composition-log.md`.
6. Require sign-off from the QA lead before moving to finalization; record approval date and approver.

## Output Expectations

- Real-time view of QA completion status.
- Auditable proof of each validation activity.
- Clear documentation of unresolved items and mitigation plans.
