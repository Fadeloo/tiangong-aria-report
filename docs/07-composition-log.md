# 07 Composition Log

Use this ledger to maintain a chronological record of drafting activity. Each entry should enable reviewers to trace what changed, why it changed, and which sources were referenced.

## Context

- Draft artifacts (`materials/output/drafts/`)
- Drafting plan (`docs/06-drafting-strategy.md`)
- Outline (`docs/05-outline.md`)
- Review feedback (`docs/08-review-notes/`)
- Automation scripts (any code under `scripts/` or `src/` leveraged during composition)

## Available Tools

- Time tracking or journaling templates (e.g., CSV, Notion, Markdown tables)
- `git diff` snapshots to capture text deltas (summarize results here, no raw dumps)
- `src.drafting.Draft.to_text` for exporting intermediate drafts
- QA checklist (`docs/10-quality-assurance-checklist.md`) to validate checkpoints

## Logging Template

| Date UTC | Contributor | Sections Touched | Tools/Commands | Source References | Notes/Outcome |
|----------|-------------|------------------|----------------|-------------------|---------------|
| YYYY-MM-DD | name | e.g., `2.1 Background` | `uv run ...` | `segment background/03` | Summary of edits, blockers, next steps |
| 2025-10-31 | Codex | I. 案例定位与战略意义 | `PYTHONPATH=. uv run python scripts/run_pipeline.py --title "清华大学环境学科人工智能引擎：可复制的高校智能教育范式"`; manual edits | SEG-210; SEG-315; SEG-084 | Generated baseline draft via pipeline and drafted Section I narrative; upcoming: restructure后续章节并补充治理与技术段落。 |
| 2025-10-31 | Codex | II. 顶层设计与治理协同; III. 人工智能技术体系 | `cat materials/output/drafts/draft.md`; `sed -n '1,200p' materials/output/drafts/draft.md` | strategy_governance/SEG-188; strategy_governance/SEG-186; strategy_governance/SEG-161; strategy_governance/SEG-078; technology_system/SEG-008; technology_system/SEG-012; technology_system/SEG-020; implementation_process/SEG-350 | Audited auto-generated sections, noted marketing filler/placeholder slides persisting in draft.md; next: rebuild governance narrative and align technical section with cited segments before writing pass. |

## Process

1. Create an entry before each drafting session noting planned focus areas.
2. Update the entry after the session with actual changes, citing source identifiers and outlining open questions.
3. Attach links to intermediate exports stored in `materials/output/drafts/` when relevant.
4. Document when `materials/output/logs/revision-directives.md` is updated and note the sections targeted.
5. Record automation usage (LLM prompts, scripts) with enough detail to reproduce results.
6. Flag dependencies on reviewer feedback so the subsequent review cycle can pick up context quickly.

## Output Expectations

- Continuous, timestamped audit trail of drafting progress.
- Clear linkage between edits, sources, and responsible contributors.
- Visibility into outstanding issues or follow-up items impacting future stages.
