# 09 Final Deliverable

Serve as the canonical record of the client-ready manuscript, including export parameters, validation checklist results, and final approvals.

## Context

- Final draft exported to `materials/output/final/deliverable.md`
- Metadata bundle (`materials/output/final/metadata.json`)
- QA checklist results (`docs/10-quality-assurance-checklist.md`)
- Review log (`docs/08-review-notes/`)
- Delivery instructions (`docs/11-delivery-guide.md`)

## Available Tools

- `src.export.DeliveryPackage` for packaging deliverables
- Style and grammar checkers (LanguageTool, Grammarly) with summarized outputs
- PDF/Word converters (via `pandoc`, `python-docx`) if alternative formats are required

## Process

1. Attach the final manuscript (Markdown plus any alternate formats) and note file paths.
2. Summarize final QA results, referencing checklist items and who validated them.
3. Confirm `materials/output/logs/revision-directives.md` has been cleared or archived after the last applied pass to avoid unintended changes.
4. Document final revisions post-review, including timestamps and responsible contributors.
5. Record metadata such as version number, word count, and delivery date.
6. Capture client approvals or sign-off statements verbatim, along with communication channel.

## Output Expectations

- Comprehensive record enabling anyone to reconstruct the delivered package.
- Confirmation that all QA and review requirements are complete.
- Clear linkage to delivery instructions and any follow-up actions.
