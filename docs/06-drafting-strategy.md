# 06 Drafting Strategy

Define how the outline will be transformed into full prose. Capture stylistic mandates, automation aids, and collaboration norms so all contributors draft consistently.

## Context

- Approved outline (`docs/05-outline.md`)
- Processed insights (`docs/04-processed-material-summary.md`)
- Tone and structural guidance (`templates/narrative/`)
- Drafting helpers (`src/drafting.py`, `src/pipeline.py`)
- Composition tracking (`docs/07-composition-log.md`)

## Available Tools

- `src.drafting.build_draft` to generate scaffolds from outline sections
- `uv run python scripts/run_pipeline.py --title "<working title>"` for automated drafts
- Language models or summarization APIs (usage logged in `docs/07-composition-log.md`)
- Style checkers (`language-tool-python`, `ruff`, custom macros)

## Process

1. Translate outline bullets into section briefs noting target length, tone, and intended audience takeaway.
2. Decide which sections will be auto-generated vs. manually authored; document rationale and fallback plans.
3. Configure drafting prompts or templates, referencing `templates/narrative/` for voice and formatting rules.
4. Establish citation practices (inline references, footnotes) and integrate them into drafting templates upfront.
5. Outline revision cadence: e.g., first pass by primary writer, second pass by fact-checker, third pass for style polish.
6. After generating an initial draft, capture section-level revision directives in `materials/output/logs/revision-directives.md` using the provided template.
7. Re-run `uv run python scripts/run_pipeline.py --title "<working title>"` to apply the directives automatically; confirm updates in `materials/output/drafts/draft.md`.
8. List automation hooks (scripts, macros) and describe how to run them, including expected inputs/outputs.
9. Capture risk mitigations (e.g., avoiding hallucinations from language models, maintaining compliance with client constraints).

## Output Expectations

- Written strategy summarizing roles, tools, and sequencing.
- Section-by-section guidance enabling another writer to continue seamlessly.
- Documented safeguards for quality, compliance, and version control.
