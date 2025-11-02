# tiangong-aria-report

tiangong-aria-report streamlines the journey from user-supplied source materials and writing briefs to publication-ready long-form documents. The repository couples a disciplined documentation trail with modular Python tooling so teams can ingest, organize, draft, review, and deliver text artifacts reproducibly.

## Key Features

- **Traceable pipeline** covering intake, organization, drafting, review, and delivery
- **Structured documentation** under `docs/` to log decisions and checkpoints
- **Dual-LLM drafting engine** that compares two model candidates per section and merges the strongest prose
- **Modular codebase** in `src/` for automation and quality enforcement
- **uv-based environment** with linting, formatting, and static typing defaults

Refer to `AGENTS.md` for detailed collaboration guidance.

## Repository Hygiene

- Runtime artifacts (everything in `materials/`), local environment files (`.env`, `.env.*`), virtual environments (e.g. `.venv/`), caches (`__pycache__/`), and log directories are ignored via `.gitignore`; keep them local to avoid leaking data or secrets.
- If any of those folders were checked in previously, remove them from the index with `git rm --cached <path>` before pushing.
- Commit only reproducible code or documentation changes; regenerate runtime data as needed after checkout.

## LLM Configuration

1. Copy `.env.example` to `.env` and populate the required secrets (`GPT5_API_KEY`, `GLM46_API_KEY`). The file is ignored by git so credentials stay local.
2. By default the pipeline calls:
	- **Primary**: `gpt-5` via OpenAI (`https://api.openai.com`), using `GPT5_API_KEY`.
	- **Secondary**: `glm-4.6` via the Zhipu open platform (`https://open.bigmodel.cn/api/paas/v4`), using `GLM46_API_KEY`.
3. Override models, base URLs, or sampling parameters through the `LLM_*` environment variables described in `src/pipeline.py` (e.g., `LLM_PRIMARY_MODEL`, `LLM_SECONDARY_BASE_URL`, `LLM_TEMPERATURE`).

All generations and scoring metadata are archived under `materials/output/logs/llm/` for auditing.
