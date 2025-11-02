# 02 Material Intake

This log tracks every asset provided for the engagement, along with its normalization status and outstanding issues. Update the table and notes below each time new materials arrive or conversion steps complete. Follow the conventions described in `docs/03-organization-plan.md`.

## Tooling Check

- `pandoc`: available at `/usr/bin/pandoc`
- `pypdf`: **missing** (`ModuleNotFoundError`). Install when PDFs arrive with `uv add pypdf`.

## Intake Summary

| identifier | original_filename | format | normalized_output | key_themes | status | notes |
|------------|-------------------|--------|-------------------|------------|--------|-------|
| INT-001 | response_1761903861983.json | json | materials/raw/response_1761903861983.json.normalized.txt | AI-enabled environmental education case study; three-layer engine architecture | normalized | Flattened page text with python3 script; HTML tables preserved for later structuring. |
| INT-002 | response_1761903897184.json | json | materials/raw/response_1761903897184.json.normalized.txt | AI empowerment project brief; funding and deployment plan for agent toolbox | normalized | Converted to sectioned text; includes budget tables requiring manual table recreation. |
| INT-003 | response_1761904025700.json | json | materials/raw/response_1761904025700.json.normalized.txt | Dynamic navigation learning model; global AI adoption examples | normalized | JSON flattened; contains marketing copy and image captions that may need trimming. |
| INT-004 | response_1761904301289.json | json | materials/raw/response_1761904301289.json.normalized.txt | AI knowledge engine presentation; environmental science applications | normalized | Section headers and image descriptions retained; review for redundant visuals. |
| INT-005 | response_1761904336509.json | json | materials/raw/response_1761904336509.json.normalized.txt | Article on AI empowering higher education; challenges and practices | normalized | Flattened to prose; citations captured in-text, verify formatting during organization. |

## Normalization Notes

- Store normalized text beside the original asset using the `.normalized.txt` suffix.
- Record transformation details (tools, command flags, manual edits) in the `notes` column.
- Archive low-quality extractions in `materials/organized/staging/` until vetted.

## Follow-ups

- Install `pypdf` as soon as any PDF assets arrive so the ingestion pipeline stays ready.
- HTML tables now converted to Markdown and image descriptions trimmed; review organized excerpts for any remaining formatting cleanup.
- Ingestion sanity check via `uv run python -c "from pathlib import Path; from src.ingestion import load_materials; load_materials(Path('materials/raw'))"` completed without errors.
