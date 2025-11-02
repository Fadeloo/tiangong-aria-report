"""Logic for organizing ingested materials into structured segments."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from .ingestion import MaterialRecord
from .utils import ensure_directory, write_text_file


@dataclass(frozen=True)
class BucketDefinition:
    """Configuration describing how a conceptual bucket should behave."""

    keywords: Tuple[str, ...]
    priority: int
    summary_hint: str


@dataclass(frozen=True)
class Segment:
    """Normalized excerpt tied to a topical bucket and source material."""

    identifier: str
    topic: str
    priority: int
    text: str
    source_path: str
    notes: str


# Buckets reflect the client deliverable structure outlined in docs/01-project-overview.md.
BUCKET_DEFINITIONS: Dict[str, BucketDefinition] = {
    "problem_context": BucketDefinition(
        keywords=(
            "痛点",
            "难点",
            "必要性",
            "意义",
            "挑战",
            "问题",
            "教育痛点",
            "strategic need",
            "pain point",
            "challenge",
            "significance",
        ),
        priority=1,
        summary_hint="Pain points,背景,以及推动AI教育变革的战略意义。",
    ),
    "strategy_governance": BucketDefinition(
        keywords=(
            "顶层设计",
            "组织机制",
            "治理",
            "政策牵引",
            "机制",
            "组织",
            "管理",
            "教务处",
            "团队",
            "协同",
            "合作",
            "教育部",
            "典型案例",
            "支持",
            "governance",
            "coordination",
            "policy",
        ),
        priority=2,
        summary_hint="顶层设计、治理体系与跨部门协同机制。",
    ),
    "technology_system": BucketDefinition(
        keywords=(
            "人工智能引擎",
            "知识引擎",
            "技术体系",
            "平台",
            "platform",
            "架构",
            "architecture",
            "结构",
            "三层",
            "双驱动",
            "模型",
            "数据",
            "算法",
            "data",
            "dataset",
            "foundation",
            "model layer",
            "knowledge base",
            "visualization",
            "知识图谱",
            "智能体",
            "agent",
            "agents",
            "tiangong",
            "toolchain",
            "数据集",
            "开源",
            "模块",
            "engine",
            "technology stack",
            "生成式人工智能",
            "deepseek",
            "gpt-5",
            "深度学习",
        ),
        priority=3,
        summary_hint="AI技术架构、模型组合与数据支撑体系。",
    ),
    "implementation_process": BucketDefinition(
        keywords=(
            "实施流程",
            "落地路径",
            "推进步骤",
            "工作流程",
            "建设路径",
            "deployment",
            "implementation",
            "流程",
            "阶段",
            "经费",
            "费用",
            "预算",
            "列支",
        ),
        priority=4,
        summary_hint="分阶段的实施路径、流程设计与推进安排。",
    ),
    "teaching_innovation": BucketDefinition(
        keywords=(
            "课堂",
            "教学",
            "课程",
            "实践",
            "实验",
            "学生",
            "教师",
            "教学案例",
            "learning scenario",
            "learning path",
            "learning paths",
            "学习路径",
            "智能学伴",
            "学习单元",
            "学习伙伴",
            "学伴",
            "自适应",
            "intelligent learning partner",
            "learning companion",
            "教学应用",
        ),
        priority=5,
        summary_hint="课堂实践、课程场景与以学生为中心的教学创新。",
    ),
    "impact_evaluation": BucketDefinition(
        keywords=(
            "成效",
            "效果",
            "成果",
            "提升",
            "指标",
            "数据",
            "完成率",
            "掌握率",
            "反馈",
            "数据看板",
            "入选",
            "表彰",
            "典型应用",
            "改进",
            "evaluation",
            "outcome",
            "impact",
        ),
        priority=6,
        summary_hint="定量与定性的教学成效、能力提升与反馈数据。",
    ),
    "sustainability_scaling": BucketDefinition(
        keywords=(
            "可持续",
            "扩展",
            "推广",
            "长期运行",
            "复制",
            "scale",
            "sustainability",
            "推广应用",
        ),
        priority=7,
        summary_hint="可持续运营策略与跨学科推广路径。",
    ),
    "challenges_mitigation": BucketDefinition(
        keywords=(
            "风险",
            "对策",
            "难题",
            "挑战",
            "问题解决",
            "瓶颈",
            "隐患",
            "mitigation",
            "lessons",
            "挑战应对",
        ),
        priority=8,
        summary_hint="风险、挑战及对应的治理与缓解策略。",
    ),
    "misc": BucketDefinition(
        keywords=("附录", "其他", "备注", "misc", "补充", "summary"),
        priority=9,
        summary_hint="暂未分类的信息，待人工复核。",
    ),
}

ADMIN_KEYWORDS: Tuple[str, ...] = (
    "申报高校",
    "填报日期",
    "填报单位",
    "填写说明",
    "请按照",
    "外文名词",
    "申报材料",
    "申报书",
    "我单位申报",
    "年 月 日",
    "承诺申明",
    "公章",
    "附件",
    "联系人",
    "联系方式",
    "填表",
    "指导语",
    "示例",
    "签章",
    "签名",
    "推理过程",
    "任务书",
)


def _normalize(text: str) -> str:
    """Return a simplified representation suitable for keyword matching."""

    return text.strip().lower()


def _clean_paragraph(paragraph: str) -> str:
    """Strip pagination markers and empty lines from a raw paragraph."""

    cleaned_lines: List[str] = []
    for line in paragraph.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# Normalized"):
            continue
        if stripped.startswith("## Page"):
            continue
        cleaned_lines.append(stripped)
    return "\n".join(cleaned_lines)


_STAGE_PATTERN = re.compile(r"^第[一二三四五六七八九十百千万0-9]+阶段$")
_ENUM_HEADING_PATTERN = re.compile(
    r"""^(
        \([一二三四五六七八九十]+\)
        |（[一二三四五六七八九十]+）
        |[一二三四五六七八九十]+\、
        |[①②③④⑤⑥⑦⑧⑨⑩]
    )""",
    re.VERBOSE,
)


def _is_stage_heading(text: str) -> bool:
    """Return whether the paragraph denotes an implementation stage heading."""

    stripped = text.strip()
    if not stripped:
        return False
    if stripped in {"推进步骤", "实施流程"}:
        return True
    if _STAGE_PATTERN.match(stripped):
        return True
    if stripped.endswith("阶段") and len(stripped) <= 12:
        return True
    return False


def _merge_stage_sequences(paragraphs: List[str]) -> List[str]:
    """Merge stage headings with their subsequent bullet descriptions."""

    merged: List[str] = []
    index = 0
    while index < len(paragraphs):
        paragraph = paragraphs[index]
        if _is_stage_heading(paragraph):
            combined: List[str] = [paragraph]
            index += 1
            while index < len(paragraphs) and not _is_stage_heading(paragraphs[index]):
                combined.append(paragraphs[index])
                index += 1
            merged.append("\n".join(combined))
            continue
        merged.append(paragraph)
        index += 1
    return merged


def _merge_enumerated_sequences(paragraphs: List[str]) -> List[str]:
    """Attach enumerated headings to their immediate descriptive paragraph."""

    merged: List[str] = []
    index = 0
    while index < len(paragraphs):
        paragraph = paragraphs[index]
        stripped = paragraph.strip()
        if _ENUM_HEADING_PATTERN.match(stripped) or any(
            stripped.startswith(prefix)
            for prefix in ("一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、")
        ):
            combined: List[str] = [paragraph]
            index += 1
            if index < len(paragraphs):
                candidate = paragraphs[index]
                candidate_stripped = candidate.strip()
                if not _ENUM_HEADING_PATTERN.match(candidate_stripped) and not _is_stage_heading(candidate_stripped):
                    combined.append(candidate)
                    index += 1
            merged.append("\n".join(combined))
            continue
        merged.append(paragraph)
        index += 1
    return merged


def _merge_short_headings(paragraphs: List[str]) -> List[str]:
    """Combine very short heading-like lines with their succeeding paragraph."""

    merged: List[str] = []
    index = 0
    while index < len(paragraphs):
        paragraph = paragraphs[index]
        stripped = paragraph.strip()
        heading_like = False
        if stripped and len(stripped) <= 6:
            first = stripped[0]
            if first.isalpha() or "\u4e00" <= first <= "\u9fff":
                heading_like = not any(char in stripped for char in (":", "：", "，", "。", "|"))

        if heading_like:
            combined = [paragraph]
            index += 1
            if index < len(paragraphs):
                combined.append(paragraphs[index])
                index += 1
            merged.append("\n".join(combined))
            continue
        merged.append(paragraph)
        index += 1
    return merged


def _merge_unfinished_paragraphs(paragraphs: List[str]) -> List[str]:
    """Merge consecutive paragraphs when the first appears truncated."""

    if not paragraphs:
        return paragraphs

    merged: List[str] = []
    index = 0
    terminal_chars = {".", "。", "！", "!", "？", "?", "；", ";", "：", ":"}

    while index < len(paragraphs):
        current = paragraphs[index]
        stripped = current.strip()
        if stripped and stripped[-1] not in terminal_chars:
            if index + 1 < len(paragraphs):
                candidate = paragraphs[index + 1]
                candidate_stripped = candidate.strip()
                if candidate_stripped and not _is_stage_heading(candidate_stripped) and not _ENUM_HEADING_PATTERN.match(candidate_stripped):
                    merged.append(current + "\n" + candidate)
                    index += 2
                    continue
        merged.append(current)
        index += 1
    return merged


def _should_skip_paragraph(paragraph: str) -> bool:
    """Return True when a paragraph should be excluded from segmentation."""

    stripped = paragraph.strip()
    if not stripped:
        return True

    normalized = stripped.lower()
    length = len(stripped)

    if length <= 2:
        return True
    if any(keyword.lower() in normalized for keyword in ADMIN_KEYWORDS) and length <= 40:
        return True
    if len(stripped.replace(" ", "")) <= 2:
        return True
    if stripped.endswith("：") and length <= 4:
        return True
    if stripped in {"承诺申明", "附件清单", "附件"}:
        return True
    if stripped.startswith("填表") and length <= 20:
        return True
    if stripped.endswith("不得出售") and length <= 20:
        return True
    if length <= 24 and _ENUM_HEADING_PATTERN.match(stripped):
        return True
    if stripped.startswith(("√", "$", "×", "□", "■")) and length <= 15:
        return True
    if length <= 20 and stripped and stripped[0] in {"(", "（"} and any(char.isdigit() for char in stripped[:6]):
        return True
    if length <= 15 and stripped.endswith("任务书"):
        return True
    if "承诺申明" in stripped or stripped.startswith("我单位申报"):
        return True
    lowered = stripped.lower()
    if "comment edit delete" in lowered or "endorse" in lowered or "unendorse" in lowered:
        return True
    return False


def _bucket_bonus(bucket: str, normalized: str) -> int:
    """Return heuristic bonus points to steer ambiguous paragraphs."""

    if bucket == "impact_evaluation":
        if any(token in normalized for token in ("%", "率", "提升", "impact", "成效", "成果", "数据", "指标")):
            return 2
    if bucket == "implementation_process":
        if "阶段" in normalized or "推进步骤" in normalized:
            return 5
        if any(token in normalized for token in ("步骤", "推进", "实施", "落地")):
            return 2
    if bucket == "strategy_governance":
        if any(token in normalized for token in ("团队", "机制", "组织", "治理", "领导", "统筹", "coordination")):
            return 1
    if bucket == "teaching_innovation":
        if any(token in normalized for token in ("学生", "课堂", "课程", "智能学伴", "学习路径", "learning path", "learning companion")):
            return 1
    return 0


def segment_materials(materials: Iterable[MaterialRecord]) -> Dict[str, List[Segment]]:
    """Group material paragraphs into topical buckets aligned with the outline.

    Parameters
    ----------
    materials:
        Iterable of normalized source artifacts loaded from `materials/raw`.

    Returns
    -------
    dict
        Mapping of bucket names to ordered lists of `Segment` instances.
    """

    segments: Dict[str, List[Segment]] = {bucket: [] for bucket in BUCKET_DEFINITIONS}
    seen_per_bucket: Dict[str, Set[str]] = {bucket: set() for bucket in BUCKET_DEFINITIONS}
    counter = 1

    for record in materials:
        raw_paragraphs = [block for block in record.content.split("\n\n") if block.strip()]
        cleaned_paragraphs = [_clean_paragraph(paragraph) for paragraph in raw_paragraphs]
        cleaned_paragraphs = [paragraph for paragraph in cleaned_paragraphs if paragraph]
        merged_paragraphs = _merge_stage_sequences(cleaned_paragraphs)
        merged_paragraphs = _merge_enumerated_sequences(merged_paragraphs)
        merged_paragraphs = _merge_short_headings(merged_paragraphs)
        merged_paragraphs = _merge_unfinished_paragraphs(merged_paragraphs)

        for paragraph in merged_paragraphs:
            if _should_skip_paragraph(paragraph):
                continue

            normalized = _normalize(paragraph)
            best_bucket = "misc"
            best_score = 0

            for bucket, definition in BUCKET_DEFINITIONS.items():
                score = sum(1 for keyword in definition.keywords if keyword.lower() in normalized)
                score += _bucket_bonus(bucket, normalized)
                if score > best_score or (score and score == best_score and definition.priority < BUCKET_DEFINITIONS[best_bucket].priority):
                    best_bucket = bucket
                    best_score = score

            identifier = f"SEG-{counter:03d}"
            counter += 1
            notes = paragraph.splitlines()[0][:120]

            if normalized in seen_per_bucket[best_bucket]:
                continue

            segments[best_bucket].append(
                Segment(
                    identifier=identifier,
                    topic=best_bucket,
                    priority=BUCKET_DEFINITIONS[best_bucket].priority,
                    text=paragraph,
                    source_path=record.identifier,
                    notes=notes,
                )
            )
            seen_per_bucket[best_bucket].add(normalized)
    # Remove empty buckets to keep downstream processing tidy.
    return {bucket: bucket_segments for bucket, bucket_segments in segments.items() if bucket_segments}


def persist_segments(segments: Dict[str, List[Segment]], destination: Path) -> None:
    """Write organized segments to disk following the canonical directory layout."""

    destination = ensure_directory(destination)
    index_rows: List[str] = ["identifier,topic,priority,notes,source_path"]

    for bucket_dir in destination.iterdir():
        if not bucket_dir.is_dir():
            continue
        if bucket_dir.name in {"staging"}:
            continue
        if bucket_dir.name not in segments:
            for existing in bucket_dir.glob("*.txt"):
                existing.unlink()

    misc_segments = segments.pop("misc", [])

    for bucket, bucket_segments in segments.items():
        bucket_dir = ensure_directory(destination / bucket)
        for existing in bucket_dir.glob("*.txt"):
            existing.unlink()

        for segment in bucket_segments:
            file_name = f"{segment.priority:02d}-{segment.identifier}.txt"
            write_text_file(bucket_dir / file_name, segment.text)
            index_rows.append(
                ",".join(
                    [
                        segment.identifier,
                        bucket,
                        str(segment.priority),
                        segment.notes.replace(",", " "),
                        segment.source_path,
                    ]
                )
            )

    if misc_segments:
        archive_dir = ensure_directory(destination / "staging" / "archived_misc")
        for existing in archive_dir.glob("*.txt"):
            existing.unlink()
        for segment in misc_segments:
            file_name = f"{segment.priority:02d}-{segment.identifier}.txt"
            write_text_file(archive_dir / file_name, segment.text)

    index_path = destination / "_index.csv"
    write_text_file(index_path, "\n".join(index_rows))
