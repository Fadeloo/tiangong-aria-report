# AGENTS.md

Guidance for AI assistants collaborating on the **tiangong-aria-report** repository.

## Project Introduction

tiangong-aria-report accelerates the transformation of heterogeneous source materials and client writing briefs into polished long-form documents. The workflow emphasizes traceability from intake through drafting, review, and delivery.

## Project Structure

```
tiangong-aria-report/
├── .claude/commands/writing/      # Optional command recipes for each writing stage
├── materials/
│   ├── raw/                       # Original assets provided by the user
│   ├── organized/                 # Curated and segmented materials ready for drafting
│   └── output/
│       ├── drafts/                # Intermediate draft exports
│       ├── final/                 # Approved deliverables
│       └── logs/                  # Processing and review logs
├── templates/
│   └── narrative/                 # Style and structure references (tone only, no text reuse)
├── docs/                          # Sequential documentation across the writing pipeline
│   ├── 01-project-overview.md
│   ├── 02-material-intake.md
│   ├── 03-organization-plan.md
│   ├── 04-processed-material-summary.md
│   ├── 05-outline.md
│   ├── 06-drafting-strategy.md
│   ├── 07-composition-log.md
│   ├── 08-review-notes/README.md
│   ├── 09-final-deliverable.md
│   ├── 10-quality-assurance-checklist.md
│   └── 11-delivery-guide.md
├── src/
│   ├── ingestion.py
│   ├── organization.py
│   ├── outline.py
│   ├── drafting.py
│   ├── review.py
│   ├── export.py
│   ├── pipeline.py
│   └── utils.py
└── scripts/
    ├── run_pipeline.py
    └── generate_report.py
```

## Workflow Commands

Follow these commands sequentially to keep writing projects reproducible:

1. `@material-intake.md` – Audit and catalogue source materials in `materials/raw/`
2. `@organization-plan.md` – Define cleaning, segmentation, and prioritization rules
3. `@outline.md` – Produce and maintain the structural outline in `docs/05-outline.md`
4. `@drafting.md` – Generate draft text using `src/drafting.py` helpers
5. `@review-cycle.md` – Capture reviewer input and revisions under `docs/08-review-notes/`
6. `@finalize.md` – Produce the delivery-ready manuscript stored in `materials/output/final/`
7. `@handoff.md` – Populate `docs/11-delivery-guide.md` with submission details

## Code Quality Standards

- **Type Hints**: All public functions require precise annotations
- **Docstrings**: Modules, classes, and functions must describe intent, inputs, outputs, and side effects
- **Static Checks**: Run `mypy src/` and `ruff check src/` before deliveries
- **Formatting**: Use `ruff format src/` to enforce consistent style
- **Logging & Errors**: Provide actionable logging and wrap risky operations with explicit exception handling

## Dependencies & Tooling

Package management uses **uv**:
- Add dependencies with `uv add <package>`
- Synchronize environment via `uv sync`
- Lockfile is `uv.lock`

Common packages:
- Text processing: pandas, numpy, nltk, rapidfuzz
- Summarization & generation: transformers, torch, accelerate (as needed)
- Quality assurance: language-tool-python, great-expectations
- Productivity: rich, typer
- Quality tools: mypy, ruff

## Script Execution

Always invoke Python scripts through uv, for example:

```
uv run python scripts/run_pipeline.py
```

## Collaboration Guidelines

### File Creation
- Create new files only when demanded by the workflow or user instructions
- Prefer editing existing assets to maintain continuity

### Documentation
- Keep numbered docs synchronized with workflow steps
- Capture decisions, references, and verification notes for audit trails

### Writing Quality
- Honor narrative style requirements in `templates/narrative/`
- Prioritize factual grounding with citations back to `materials/`
- Track revision rationales in `docs/08-review-notes/`

### Git Workflow
- Do not commit without explicit user approval
- When committing, craft descriptive messages aligned with repository conventions
- Keep `.env`, `.env.*`, local virtual environments, `__pycache__/`, and every directory under `materials/` (raw intake, organized segments, generated outputs) out of version control—these paths are ignored by `.gitignore` and must never be re-added
- If any of those artifacts were previously tracked, run `git rm --cached <path>` to drop them before pushing
