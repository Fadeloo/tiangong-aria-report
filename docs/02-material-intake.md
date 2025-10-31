# 02 Material Intake

This log tracks every asset provided for the engagement, along with its normalization status and outstanding issues. Update the table and notes below each time new materials arrive or conversion steps complete. Follow the conventions described in `docs/03-organization-plan.md`.

## Tooling Check

- `pandoc`: available at `/usr/bin/pandoc`
- `pypdf`: **missing** (`ModuleNotFoundError`). Install when PDFs arrive with `uv add pypdf`.

## Intake Summary

| identifier | original_filename | format | normalized_output | key_themes | status | notes |
|------------|-------------------|--------|-------------------|------------|--------|-------|
| _pending_  | –                 | –      | –                 | –          | waiting| No source files ingested yet. |

## Normalization Notes

- Store normalized text beside the original asset using the `.normalized.txt` suffix.
- Record transformation details (tools, command flags, manual edits) in the `notes` column.
- Archive low-quality extractions in `materials/organized/staging/` until vetted.

## Follow-ups

- Install `pypdf` before processing PDFs.
- Update the table above once raw materials populate `materials/raw/`.
