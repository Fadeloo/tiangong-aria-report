# 08 Review Notes

Centralize reviewer feedback, decision logs, and resolution status for every cycle. Use subfolders to isolate distinct review passes (e.g., `cycle-01-internal`, `cycle-02-client`).

## Context

- Current draft (`materials/output/drafts/draft.md`)
- Review exports generated via `src/review.py`
- QA checklist (`docs/10-quality-assurance-checklist.md`)
- Composition log (`docs/07-composition-log.md`)
- Issue trackers or ticket references linked to this project

## Available Tools

- `src.review.ReviewComment` and `export_review_notes`
- Shared annotation platforms (Google Docs, Notion, GitHub pull requests)
- Triage labels (`blocker`, `major`, `minor`, `nit`) standardized in drafting strategy

## Process

1. Create a new subfolder per review cycle containing:
   - `summary.md` for high-level findings
   - `comments.md` exported from `ReviewComment` helpers
   - Optional attachments (annotated PDFs, screenshots)
2. Log each piece of feedback with author, timestamp, severity, affected section, and source reference.
3. Mirror decisions and resolutions back to `docs/07-composition-log.md`, ensuring bi-directional traceability.
4. For actionable revisions, translate feedback into section updates within `materials/output/logs/revision-directives.md` so the next drafting run incorporates them.
5. For blockers, open an explicit follow-up item and track until closed; note closure date and validator.
6. After incorporating revisions, update `docs/10-quality-assurance-checklist.md` to reflect re-run validations.

## Output Expectations

- Organized archive of review cycles ready for audits.
- Clear mapping from feedback to implemented changes.
- Documented approvals and outstanding issues before finalization.
