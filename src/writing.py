"""Higher-level writing orchestration layered on top of LLM clients."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from .llm import LLMClient, LLMError, LLMGeneration, LLMGenerationPrompt
from .organization import Segment
from .outline import OutlineSection
from .utils import ensure_directory, write_text_file

LOGGER = logging.getLogger(__name__)
_WORD_PATTERN = re.compile(r"[A-Za-z0-9\u4e00-\u9fa5]{2,}")


@dataclass
class SectionWriterConfig:
    """Tunable parameters controlling multi-model section generation."""

    temperature: float = 0.3
    max_output_tokens: int = 800
    top_p: float = 0.9
    language: str = "zh"
    log_dir: Path | None = None
    max_context_segments: int = 10
    min_paragraph_score: float = 0.25


@dataclass
class _CandidateRecord:
    """Container bundling a completed generation with its evaluation score."""

    client_id: str
    generation: LLMGeneration
    score: float


class DualLLMSectionWriter:
    """Request two models, reconcile their responses, and return a merged section."""

    def __init__(self, primary: LLMClient, secondary: LLMClient, config: SectionWriterConfig) -> None:
        self._primary = primary
        self._secondary = secondary
        self._config = config
        self._log_dir = ensure_directory(config.log_dir) if config.log_dir else None

    def write_section(self, section: OutlineSection, segments: Sequence[Segment]) -> str:
        """Generate prose for the supplied outline section using two LLMs."""

        prompt = self._build_prompt(section, segments)
        candidates: List[_CandidateRecord] = []

        for client in (self._primary, self._secondary):
            try:
                generation = client.generate(prompt)
            except LLMError as exc:
                LOGGER.error(
                    "LLM %s failed to generate section '%s': %s",
                    client.identifier,
                    section.title,
                    exc,
                )
                continue
            score = self._score_generation(generation.text, segments)
            candidates.append(_CandidateRecord(client_id=client.identifier, generation=generation, score=score))

        if not candidates:
            LOGGER.error(
                "Both LLM invocations failed for section '%s'; falling back to stitched source segments.",
                section.title,
            )
            return self._fallback_from_segments(segments)

        merged = self._merge_candidates(section, segments, candidates)
        self._persist_logs(section, candidates, merged)
        return merged

    def _build_prompt(self, section: OutlineSection, segments: Sequence[Segment]) -> LLMGenerationPrompt:
        context_segments = sorted(segments, key=lambda seg: seg.priority)[: self._config.max_context_segments]
        bullet_lines = "\n".join(f"- {bullet}" for bullet in section.bullet_points if bullet)
        excerpt_lines = "\n".join(f"[{segment.identifier}] {segment.text}" for segment in context_segments)

        instruction_language = "中文" if self._config.language.lower().startswith("zh") else "English"
        system_prompt = (
            "You are an expert educational transformation writer. Compose well-structured, factual prose, "
            "avoiding plagiarism while grounding claims in the provided excerpts."
        )
        user_prompt = (
            f"Please draft the section '{section.title}' in {instruction_language}.\n\n"
            f"Outline anchor points:\n{bullet_lines or '- (No bullets extracted)'}\n\n"
            "Source excerpts (reference identifiers in brackets where relevant):\n"
            f"{excerpt_lines or '(No supporting segments available)'}\n\n"
            "Write cohesive paragraphs (no bullet lists) that synthesize the ideas, cite identifiers in square brackets"
            " when drawing directly from an excerpt, and include transitional language for flow."
        )

        return LLMGenerationPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self._config.temperature,
            max_output_tokens=self._config.max_output_tokens,
            top_p=self._config.top_p,
        )

    def _score_generation(self, text: str, segments: Sequence[Segment]) -> float:
        if not text.strip():
            return 0.0
        keyword_score = self._keyword_coverage_score(text, segments)
        length_bonus = min(len(text) / 600.0, 2.0)
        paragraph_bonus = 0.3 * max(len(self._extract_paragraphs(text)) - 1, 0)
        return keyword_score * 5.0 + length_bonus + paragraph_bonus

    def _merge_candidates(
        self,
        section: OutlineSection,
        segments: Sequence[Segment],
        candidates: Sequence[_CandidateRecord],
    ) -> str:
        best_candidate = max(candidates, key=lambda candidate: candidate.score)
        merged_paragraphs = self._extract_paragraphs(best_candidate.generation.text)
        merged_set = {paragraph.strip() for paragraph in merged_paragraphs}

        for candidate in sorted(candidates, key=lambda candidate: candidate.score, reverse=True):
            if candidate is best_candidate:
                continue
            for paragraph in self._extract_paragraphs(candidate.generation.text):
                normalized = paragraph.strip()
                if not normalized or normalized in merged_set:
                    continue
                para_score = self._paragraph_score(normalized, segments)
                if para_score < self._config.min_paragraph_score:
                    continue
                merged_paragraphs.append(normalized)
                merged_set.add(normalized)

        if not merged_paragraphs:
            LOGGER.warning("Section '%s' produced empty paragraphs; using fallback.", section.title)
            return self._fallback_from_segments(segments)

        return "\n\n".join(merged_paragraphs)

    def _paragraph_score(self, paragraph: str, segments: Sequence[Segment]) -> float:
        base = self._keyword_coverage_score(paragraph, segments)
        length_factor = min(len(paragraph) / 400.0, 1.0)
        return base * 3.0 + length_factor

    def _keyword_coverage_score(self, text: str, segments: Sequence[Segment]) -> float:
        keywords = self._segment_keywords(segments)
        if not keywords:
            return 0.0
        lower_text = text.lower()
        hits = sum(1 for keyword in keywords if keyword in lower_text)
        return hits / len(keywords)

    def _segment_keywords(self, segments: Sequence[Segment]) -> set[str]:
        keywords: set[str] = set()
        for segment in segments:
            for match in _WORD_PATTERN.findall(segment.text.lower()):
                if len(match) <= 2:
                    continue
                keywords.add(match)
        return keywords

    def _extract_paragraphs(self, text: str) -> List[str]:
        return [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]

    def _fallback_from_segments(self, segments: Sequence[Segment]) -> str:
        if not segments:
            return "TODO: Awaiting content"
        ordered = sorted(segments, key=lambda seg: (seg.priority, seg.identifier))
        return "\n\n".join(segment.text for segment in ordered)

    def _persist_logs(
        self,
        section: OutlineSection,
        candidates: Sequence[_CandidateRecord],
        merged_text: str,
    ) -> None:
        if not self._log_dir:
            return
        section_dir = ensure_directory(self._log_dir / self._slugify(section.title))
        for candidate in candidates:
            file_name = f"{candidate.client_id}-{self._slugify(candidate.generation.model)}.md"
            write_text_file(section_dir / file_name, candidate.generation.text)
        metadata = {
            "section": section.title,
            "language": self._config.language,
            "candidates": [
                {
                    "client_id": candidate.client_id,
                    "model": candidate.generation.model,
                    "provider": candidate.generation.provider,
                    "score": round(candidate.score, 4),
                }
                for candidate in candidates
            ],
            "merged_length": len(merged_text),
        }
        write_text_file(section_dir / "merged.md", merged_text)
        write_text_file(
            section_dir / "metadata.json",
            json.dumps(metadata, ensure_ascii=False, indent=2),
        )

    def _slugify(self, value: str) -> str:
        sanitized = re.sub(r"[^A-Za-z0-9\u4e00-\u9fa5]+", "-", value.strip()).strip("-")
        if not sanitized:
            return "section"
        return sanitized.lower()