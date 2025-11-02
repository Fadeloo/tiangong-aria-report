"""High-level orchestration for the tiangong-aria-report workflow."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Set

from .drafting import Draft, SectionWriter, build_draft, save_draft
from .export import DeliveryPackage
from .ingestion import load_materials
from .organization import persist_segments, segment_materials
from .outline import generate_outline
from .revision import apply_revision_directives
from .llm import LLMClientConfig, LLMError, OpenAICompatibleClient
from .writing import DualLLMSectionWriter, SectionWriterConfig

LOGGER = logging.getLogger(__name__)
GLM_DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
_LOADED_ENV_PATHS: Set[Path] = set()


def _optional_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value == "":
        return None
    return value


def _get_env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        LOGGER.warning("Environment variable %s=%s is not a valid float; using %s", name, raw, default)
        return default


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        LOGGER.warning("Environment variable %s=%s is not a valid integer; using %s", name, raw, default)
        return default


def _load_env_file(base_path: Path) -> None:
    env_path = base_path / ".env"
    if env_path in _LOADED_ENV_PATHS:
        return
    if not env_path.exists():
        return
    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                LOGGER.warning("Ignoring malformed env line in %s: %s", env_path, raw_line)
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                os.environ.setdefault(key, value)
        _LOADED_ENV_PATHS.add(env_path)
    except OSError as exc:
        LOGGER.warning("Unable to read environment file %s: %s", env_path, exc)


@dataclass
class PipelineConfig:
    """Configuration describing filesystem layout for the pipeline."""

    title: str
    raw_dir: Path
    organized_dir: Path
    draft_path: Path
    final_dir: Path
    revision_directives_path: Path
    llm: "LLMOrchestrationConfig"


@dataclass
class LLMOrchestrationConfig:
    """LLM wiring details used to generate section-level prose."""

    primary: LLMClientConfig
    secondary: LLMClientConfig
    temperature: float = 0.3
    max_output_tokens: int = 800
    top_p: float = 0.9
    language: str = "zh"
    log_dir: Path | None = None
    max_context_segments: int = 10
    min_paragraph_score: float = 0.25

    @classmethod
    def from_env(cls, base_path: Path) -> "LLMOrchestrationConfig":
        """Construct configuration by inspecting environment variables."""
        primary = LLMClientConfig(
            identifier=os.getenv("LLM_PRIMARY_ID", "gpt5"),
            model=os.getenv("LLM_PRIMARY_MODEL", "gpt-5"),
            provider=os.getenv("LLM_PRIMARY_PROVIDER", "openai"),
            api_key_env=os.getenv("LLM_PRIMARY_API_KEY_ENV", "GPT5_API_KEY"),
            api_key=_optional_env("LLM_PRIMARY_API_KEY"),
            base_url=_optional_env("LLM_PRIMARY_BASE_URL"),
        )
        secondary_base_url = _optional_env("LLM_SECONDARY_BASE_URL") or GLM_DEFAULT_BASE_URL
        secondary = LLMClientConfig(
            identifier=os.getenv("LLM_SECONDARY_ID", "glm46"),
            model=os.getenv("LLM_SECONDARY_MODEL", "glm-4.6"),
            provider=os.getenv("LLM_SECONDARY_PROVIDER", "openai-compatible"),
            api_key_env=os.getenv("LLM_SECONDARY_API_KEY_ENV", "GLM46_API_KEY"),
            api_key=_optional_env("LLM_SECONDARY_API_KEY"),
            base_url=secondary_base_url,
        )

        temperature = _get_env_float("LLM_TEMPERATURE", 0.3)
        max_output_tokens = _get_env_int("LLM_MAX_OUTPUT_TOKENS", 900)
        top_p = _get_env_float("LLM_TOP_P", 0.9)
        language = os.getenv("LLM_PROMPT_LANGUAGE", "zh")
        max_context_segments = _get_env_int("LLM_MAX_CONTEXT_SEGMENTS", 10)
        min_paragraph_score = _get_env_float("LLM_MIN_PARAGRAPH_SCORE", 0.25)

        log_dir_env = _optional_env("LLM_LOG_DIR")
        log_dir = Path(log_dir_env) if log_dir_env else base_path / "materials" / "output" / "logs" / "llm"

        return cls(
            primary=primary,
            secondary=secondary,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            language=language,
            log_dir=log_dir,
            max_context_segments=max_context_segments,
            min_paragraph_score=min_paragraph_score,
        )


class WritingPipeline:
    """Orchestrate the end-to-end document creation workflow."""

    def __init__(self, config: PipelineConfig, section_writer: Optional[SectionWriter] = None) -> None:
        self.config = config
        self.section_writer = section_writer or self._build_section_writer()

    def run(self, metadata_overrides: Optional[Dict[str, str]] = None) -> DeliveryPackage:
        """Execute the pipeline and return a delivery package."""

        materials = load_materials(self.config.raw_dir)
        segments = segment_materials(materials)
        persist_segments(segments, self.config.organized_dir)

        outline = generate_outline(segments)
        draft = build_draft(outline, segments, self.config.title, section_writer=self.section_writer)
        draft = apply_revision_directives(draft, self.config.revision_directives_path)
        save_draft(draft, self.config.draft_path)

        metadata: Dict[str, str] = {
            "title": self.config.title,
            "materials_count": str(len(materials)),
            "sections": str(len(draft.sections)),
        }
        if metadata_overrides:
            metadata.update(metadata_overrides)

        package = DeliveryPackage(draft=draft, metadata=metadata)
        package.write(self.config.final_dir)
        return package

    def _build_section_writer(self) -> SectionWriter:
        try:
            primary_client = self._create_client(self.config.llm.primary)
            secondary_client = self._create_client(self.config.llm.secondary)
        except LLMError as exc:
            raise RuntimeError(f"Failed to initialise LLM clients: {exc}") from exc

        writer_config = SectionWriterConfig(
            temperature=self.config.llm.temperature,
            max_output_tokens=self.config.llm.max_output_tokens,
            top_p=self.config.llm.top_p,
            language=self.config.llm.language,
            log_dir=self.config.llm.log_dir,
            max_context_segments=self.config.llm.max_context_segments,
            min_paragraph_score=self.config.llm.min_paragraph_score,
        )
        return DualLLMSectionWriter(primary_client, secondary_client, writer_config)

    def _create_client(self, config: LLMClientConfig) -> OpenAICompatibleClient:
        if config.provider in {"openai", "openai-compatible"}:
            return OpenAICompatibleClient(config)
        raise LLMError(f"Unsupported LLM provider '{config.provider}' for client '{config.identifier}'.")


def default_config(base_path: Path, title: str) -> PipelineConfig:
    """Construct a PipelineConfig rooted at the given base path."""
    _load_env_file(base_path)
    return PipelineConfig(
        title=title,
        raw_dir=base_path / "materials" / "raw",
        organized_dir=base_path / "materials" / "organized",
        draft_path=base_path / "materials" / "output" / "drafts" / "draft.md",
        final_dir=base_path / "materials" / "output" / "final",
        revision_directives_path=base_path / "materials" / "output" / "logs" / "revision-directives.md",
        llm=LLMOrchestrationConfig.from_env(base_path),
    )


def run_default(base_path: Path, title: str, metadata_overrides: Optional[Dict[str, str]] = None) -> DeliveryPackage:
    """Convenience helper to execute the pipeline given a root path and title."""

    pipeline = WritingPipeline(default_config(base_path, title))
    return pipeline.run(metadata_overrides=metadata_overrides)
