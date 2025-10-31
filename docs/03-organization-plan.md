# 03 Organization Plan

This plan details how heterogeneous source materials are normalized, segmented, and promoted through the tiangong-aria-report workflow. All steps assume that client requirements are captured in `docs/01-project-overview.md` and that raw assets are supplied under `materials/raw/`.

## Source Normalization Strategy

- Acceptable incoming formats: `.txt`, `.md`, `.json`, `.pdf`, `.docx`. Normalize everything to UTF-8 text before ingestion.
- Preferred toolchain:
  - `pandoc` or `python-docx` via `uv run` for Word documents.
  - `pypdf` or `pdfminer.six` via an ad-hoc extraction script for PDF files.
  - `jq` or a short Python script to flatten JSON records into readable bullet lists.
  - Manual cleanup for Markdown to strip navigation or boilerplate blocks.
- Save normalized text beside its source using the suffix `source-name.normalized.txt`. Archive the original asset untouched.
- Track every normalized file in `docs/02-material-intake.md`, including origin, transformation notes, and confidence in text fidelity.

## Organized Directory Layout

- `materials/organized/_index.csv`: master index containing `identifier`, `topic`, `priority`, `notes`, and `source_path`.
- `materials/organized/{topic}/`: folder per topical bucket. Files follow `{priority:02d}-{identifier}.txt`.
- `materials/organized/staging/`: temporary workspace for partially cleaned excerpts. Clear before committing to the main buckets.
- Logs produced during segmentation should be captured in `materials/output/logs/organization-YYYYMMDD.md` for auditability.

## Workflow Command Playbooks

### `@material-intake.md`

**Context**
- `docs/01-project-overview.md`
- `docs/02-material-intake.md`
- Raw assets under `materials/raw/`
- Normalization scripts under `src/ingestion.py` and ad-hoc converters in `scripts/`

**Available Tools**
- `uv run python scripts/run_pipeline.py --title "<working title>" --base-path .` (dry run to confirm ingestion)
- `src.ingestion.load_materials` for validating UTF-8 conversion
- External converters (`pandoc`, `python-docx`, `pypdf`, `jq`) as needed

**Process**
1. Catalogue every provided asset in `docs/02-material-intake.md`, recording filename, format, key themes, and any conversion blockers.
2. Normalize non-plain-text materials to `.txt` using the toolchain above; store alongside originals.
3. Run `uv run python -c "from src.ingestion import load_materials; load_materials(Path('materials/raw'))"` to ensure all files load without error.
4. Flag gaps or low-quality sources in the intake log so downstream stages know which materials require corroboration.

### `@organization-plan.md`

**Context**
- This document (`docs/03-organization-plan.md`)
- Normalized materials in `materials/raw/`
- Segmentation helpers in `src/organization.py`

**Available Tools**
- `src.organization.segment_materials` and `persist_segments`
- `uv run python -m src.pipeline` components for quick prototypes
- Spreadsheet or Obsidian table views for topical clustering (optional)

**Process**
1. Define topical buckets aligned with the client objectives (e.g., `background`, `requirements`, `analysis`, `recommendations`). Update the keyword map in `src/organization.py` if necessary.
2. Use a short Python notebook or script to preview `segment_materials` output and iteratively refine keyword rules.
3. Persist canonical segments with `persist_segments`, then relocate files into the `{topic}/` folders using the naming convention described above.
4. Populate `materials/organized/_index.csv` with one row per segment, noting the originating source and a short summary line.
5. Summarize prioritization logic in this document so future collaborators understand why certain sources rank higher.

### `@outline.md`

**Context**
- Organized segments in `materials/organized/`
- `docs/05-outline.md`
- Outline helpers in `src/outline.py`
- Narrative guidance in `templates/narrative/`

**Available Tools**
- `src.outline.generate_outline` to bootstrap structure
- Mind-mapping or outlining software for manual refinement
- `docs/04-processed-material-summary.md` for quick reference summaries

**Process**
1. Review `materials/organized/_index.csv` to identify must-include themes and supporting evidence.
2. Run `generate_outline` against the consolidated segments to create an initial `OutlinePlan`.
3. Manually expand or reorder sections in `docs/05-outline.md`, ensuring every high-priority segment is mapped to a heading.
4. Annotate each outline bullet with traceability back to source identifiers so the drafting stage can cite confidently.

### `@drafting.md`

**Context**
- Approved outline from `docs/05-outline.md`
- Organized segment text files
- Drafting utilities in `src/drafting.py`
- Draft workspace `materials/output/drafts/`

**Available Tools**
- `src.drafting.build_draft` and `Draft.to_text`
- `uv run python scripts/run_pipeline.py --title "<working title>"` for automated scaffolds
- Language models or summarization tools (must log usage in `docs/07-composition-log.md`)

**Process**
1. Prepare a `segment_lookup` dictionary keyed by outline headings to the relevant organized text.
2. Use `build_draft` to assemble a baseline draft; export to `materials/output/drafts/draft.md`.
3. Capture revision directives in `materials/output/logs/revision-directives.md` whenever section-level rewrites are needed, then rerun the pipeline to regenerate the draft with updates applied.
4. Iterate manually within `docs/07-composition-log.md`, documenting major revisions, reasoning, and references.
5. Ensure the draft reflects tone and structural requirements specified in `docs/01-project-overview.md` and `templates/narrative/`.

### `@review-cycle.md`

**Context**
- Draft under review (`materials/output/drafts/draft.md`)
- Feedback tracker `docs/08-review-notes/`
- Review utilities in `src/review.py`
- Stakeholder comments or issue tracker exports

**Available Tools**
- `src.review.ReviewComment` and `export_review_notes`
- Shared review platforms (Google Docs, Notion) with notes synced back to the repo
- `docs/10-quality-assurance-checklist.md` to structure QA passes

**Process**
1. Gather reviewer input and normalize severity labels (`blocker`, `major`, `minor`, `nit`).
2. Add each comment to a `ReviewComment` list and export markdown snapshots to `docs/08-review-notes/DATE.md`.
3. Track resolution status in `docs/07-composition-log.md`, linking to the corresponding review entry.
4. Re-run the QA checklist after addressing feedback to confirm no regressions were introduced.

### `@finalize.md`

**Context**
- Polished draft (`materials/output/drafts/draft.md`)
- `materials/output/final/`
- Export helpers in `src/export.py`
- QA guide `docs/10-quality-assurance-checklist.md`

**Available Tools**
- `src.export.DeliveryPackage.write`
- `uv run python scripts/generate_report.py --title "<final title>" --meta key=value`
- `mypy src/`, `ruff check src/`, and `ruff format src/`

**Process**
1. Freeze the final manuscript, ensuring all citations reference `materials/organized/` identifiers.
2. Execute `mypy` and `ruff` to guarantee tooling compliance before packaging.
3. Use `generate_report.py` (or `run_pipeline.py`) to emit the final markdown and metadata JSON into `materials/output/final/`.
4. Record delivery metadata (client, date, version tag) in `materials/output/logs/finalization-YYYYMMDD.md` and summarize decisions in `docs/09-final-deliverable.md`.

### `@handoff.md`

**Context**
- Final deliverable (`materials/output/final/deliverable.md`)
- Metadata (`materials/output/final/metadata.json`)
- Delivery guide `docs/11-delivery-guide.md`
- Any ancillary assets (figures, appendices) referenced in the final manuscript

**Available Tools**
- `docs/11-delivery-guide.md` template
- Repository changelog or issue tracker for release notes
- Archival scripts (if required by the client)

**Process**
1. Populate `docs/11-delivery-guide.md` with delivery method, file list, version history, and follow-up actions.
2. Double-check that all referenced materials are accessible and linked (e.g., appendix files, data tables).
3. Package the final bundle according to client instructions (ZIP archive, shared drive upload, etc.) and note the destination.
4. Close the engagement by updating `docs/09-final-deliverable.md` with confirmation of handoff and any outstanding to-dos.

This organization plan should be revisited whenever new material types are introduced or when the pipeline logic in `src/` evolves.
