# 06 Drafting Strategy

本策略明确《北京人工智能教育蓝皮书》清华大学环境学科人工智能引擎典型案例的写作分工、流程、自动化节奏与质量护栏，保障任何协作成员均可延续当前进度完成 6000–8000 字的长文初稿与迭代。

## 1. 项目概览与角色

- **工作标题**：`清华大学环境学科人工智能引擎：可复制的高校智能教育范式`
- **语体基调**：政策导向、严谨、以治理逻辑带动技术与教学场景描述。段内采用短段+数据支撑，避免宣传口吻。
- **读者预期**：教育行政部门、校级教改负责人、环境与工程类高校教师。
- **核心角色**
  - `Primary Writer`：负责 I、IV、VI、VIII 章节的主文本；整合 fact-check 结果。
  - `Automation Specialist`：维护 `src/drafting.py`、`scripts/run_pipeline.py` 自动草稿及段落拼接；生成 revision directives。
  - `Fact Checker`：核对量化指标、政策引用与段落引用的 `SEG-` 号来源，更新 `docs/07-composition-log.md`。
  - `Style Editor`（可由 Primary Writer 兼任）：执行语言、格式、段落转接润色，并运行语言与质量工具。

## 2. 章节任务分解

| 大纲章节 | 目标字数 | 重点信息 & 证据段 | 风格 & 读者收获 | 主撰责任 | 自动化策略 |
|----------|----------|------------------|----------------|----------|-------------|
| I. 案例定位与战略意义 | 800–900 | SEG-210（挑战）、SEG-315（系统性融入）、SEG-084（国际对标） | 开篇以政策语态说明痛点，结尾让决策者看到“为何现在必须行动”。 | Primary Writer | 手工撰写，需建立问题—回应结构并嵌入对标案例短侧栏 |
| II. 顶层设计与治理协同 | 900–1000 | SEG-188、SEG-186、SEG-161 + SEG-078（外部标杆） | 表达治理闭环，凸显“部门职责分工 + 政策背书”，读者收获治理模板。 | Automation Specialist初稿 + writer润色 | `build_draft` 生成框架，人工补写治理机制图示描述及政策话语 |
| III. 人工智能技术体系 | 1100–1200 | SEG-008、SEG-012/013、SEG-009（界面说明）、SEG-020、SEG-350 | 技术说明需兼顾非技术读者，可复制的三层架构 + 学伴体验，提供部署蓝图。 | Automation Specialist | 自动生成主体，手动补充双驱动逻辑和“24小时智能学伴”故事化引子 |
| IV. 实施路径与组织保障 | 950–1100 | SEG-350、SEG-149、SEG-095、SEG-057/058/059、SEG-046 | 以阶段时间线和资源配置说服管理层，突出实施步骤可追溯。 | Primary Writer | 手写分阶段叙事与经费表述，引用自动草稿中的流程要素 |
| V. 教学场景与应用创新 | 850–950 | SEG-004、SEG-029、SEG-130、SEG-046（案例） | 讲述课堂变革与师生体验，读者应理解“如何用”。 | Automation Specialist | 自动草稿基础上补充真实课堂对话描写、教师反馈 |
| VI. 成效评估与价值证明 | 900–1000 | SEG-087、SEG-026/027、SEG-035、SEG-045（质性）、SEG-037（用户基数） | 采用报告化口吻，提供指标矩阵，让政策层看到量化成果。 | Primary Writer | 手工整合量化指标 + 质性评价表格，避免数据散点 |
| VII. 可持续运营与推广路径 | 650–750 | SEG-092、SEG-007、SEG-037、SEG-051、SEG-056 | 聚焦复制路径和推广资源，输出路线图式描述。 | Automation Specialist | 自动生成框架，人工补齐推广节奏时间线 |
| VIII. 风险挑战与应对策略 | 600–700 | SEG-040、SEG-041、SEG-317、SEG-095、SEG-351、SEG-077 | 控制在政策合规语态中给出“风险→机制”对照表，读者收获治理清单。 | Primary Writer | 手写，围绕“技术/伦理/教学三重风险”结构化呈现 |

- **Fallback 约定**：若自动生成段落缺乏关键数据（如 III 章缺少界面描写），由 Primary Writer 在 `materials/organized/` 中追加段落并直接手写；若手写段落超过目标字数 ±15%，由 Automation Specialist 通过 prompt 重写压缩篇幅。
- 所有章节完成后，统一使用 `Primary Writer` 的语态检查，确保段落转接自然。

- 如需新增“结语”或“附录”，由 Primary Writer 根据篇幅灵活添加（目标 200–300 字），引用整体价值总结与推广建议。

## 3. 草稿生成与手工写作流程

1. **准备段落素材**
   - 运行 `uv run python scripts/run_pipeline.py --title "清华大学环境学科人工智能引擎：可复制的高校智能教育范式"`。首次执行前先复制 `.env.example` 为 `.env`，填入 `GPT5_API_KEY` 与 `GLM46_API_KEY`，分别对应 OpenAI 的 `gpt-5` 与智谱开放平台的 `glm-4.6`。
   - `DualLLMSectionWriter` 会为每个章节并行请求两种模型，自动挑选得分更高的段落写入 `materials/output/drafts/draft.md`，并在 `materials/output/logs/llm/<section>/` 中保存候选文本与评分，方便追踪与比对。
   - 如需局部预览，可在 `python` REPL 中手动实例化 `DualLLMSectionWriter`（或替换为自定义 writer）后调用 `build_draft(..., section_writer=writer)`，传入筛选后的 `segment_lookup`。

2. **手工撰写与混合编辑**
   - Primary Writer 在 `materials/output/drafts/draft.md` 上开 `feature` 分支式编辑，对 LLM 生成段落进行事实核对、风格统一，必要时补写 `SEG-` 引用或修改标注。
   - 叙述节奏：每个一级标题 3–4 个小节（无需另设二级标题，使用加粗句首或列表呈现），确保“问题→举措→成效/启示”闭环。
   - 对国际对标、师生反馈等故事化段落，采用“案例快照”格式（50–80 字）并紧邻定量数据。

3. **引用与证据管理**
   - 所有事实或数据必须绑定 `SEG-` 段号；无现成证据时记录于 `docs/07-composition-log.md` 的 `Follow-up` 栏，标注“待补充来源”。
   - 若引用多段支持，可合并写作：`（参见 SEG-008，SEG-013）`。
   - 表格引用（如预算、指标）以 Markdown 表格呈现，表头含“数据来源：SEG-xxx”。若需交叉验证，在脚注处写 `注：数字与SEG-xxx对齐，待学校确认。`

## 4. 模板与提示词设定

- **叙事模板（适用于重点段落）**
  ```markdown
  **关键命题句。** 段落首句明确该段落主旨，直接对接章节副标题。
  — 证据描述：整合两条以上数据或制度设计要素，以并列或递进句式展开。
  — 场景描写：加入1–2句课堂或管理层面细节。
  — 归纳句：强调可复制性或推广启示。
  （参见 SEG-xxx）
  ```
- **自动化提示词样例（供 LLM 或内置脚本二次生成）**

  > 请依据以下要素撰写“顶层设计与治理协同”章节的“跨部门协同机制”段落，字数 180 左右，语言保持政策文件风格：\n> - 依托资料 `SEG-188`、`SEG-186`、`SEG-161`\n> - 强调教务处、学堂在线、秀钟书院的分工\n> - 补充“教育部典型案例”背书语句\n> - 以“形成‘战略规划—平台运营—教学落地’闭环”为收束\n> 输出 Markdown 段落并附 `（参见 SEG-xxx）` 风格引用。

- **语料风格对齐**：参考 `templates/narrative/`（目前为空，可后续补入 tone 指南）。暂以 `docs/01-project-overview.md` 中“结构化、逻辑清晰、避免堆砌术语”要求为基线。

## 5. 修订节奏与追踪

1. **初稿完成后**：
   - 在 `materials/output/logs/revision-directives.md` 中记录指令，使用模板：
     ```markdown
     # （可选）新标题
     ## I. 案例定位与战略意义
     - 调整开篇问题陈述，突出“环境学科”关键词
     - 补充国际对标小结（SEG-084）
     
     ## VI. 成效评估与价值证明
     更新核心指标表，将“问题回答量”与“学情看板”两组数据合并。
     ```
   - 运行 `uv run python scripts/run_pipeline.py --title "..."` 使修订自动写回 `materials/output/drafts/draft.md`，并比对最新更新时间确认覆盖成功。
   - 变更说明记录到 `docs/07-composition-log.md`；列出命令、改动章节、对应 `SEG-` 来源。

2. **复核节奏**
   - `Primary Writer` → `Fact Checker` → `Style Editor` 顺序，首次循环以 24 小时为间隔。
   - 每轮完成后执行：
     - `ruff format materials/output/drafts/draft.md`
     - `uv run python -m language_tool_python`（如环境支持）或手动调用 Grammarly 类工具。
     - 重要数字交叉验证（至少两名成员签名于 `docs/07-composition-log.md` 的备注栏）。

3. **与审稿流程衔接**
   - 审稿意见统一收敛至 `docs/08-review-notes/` 新建文件（日期命名），同时在 revision directives 中同步可操作事项。
   - 若审稿新增资料，需要回溯 `materials/organized/` 并打标签，保证 traceability。

## 6. 自动化脚本与运行说明

- `uv run python scripts/run_pipeline.py --title "<working title>"`：端到端刷新草稿、提要和元数据，默认覆盖 `materials/output/drafts/draft.md`。
- `uv run python -c "from src.drafting import build_draft; ..." `：用于局部调试段落组合，需显式传入 `segment_lookup`。
- `uv run python scripts/generate_report.py --title "<final title>"`：最终交付打包前运行，写入 `materials/output/final/`。
- 所有自动化操作完成后务必在 `docs/07-composition-log.md` 记录命令、时间、输出文件路径。
- 若脚本报错，先检查 `materials/organized/_index.csv` 是否存在缺失字段，再查看 `src/organization.BUCKET_DEFINITIONS` 是否需要补充关键词。

## 7. 风险与缓解措施

- **信息失真**：LLM 或自动拼接可能误组装跨段内容。缓解：每段落写完后与 `SEG-` 原文对照；关键数据在 `materials/organized/` 中复制简短原句比对。
- **政策合规与措辞风险**：避免夸大“首创”“唯一”等敏感词，Style Editor 设定关键词过滤（可在文本编辑器内搜索“唯一”、“首次”等）。
- **数据时效性**：如需引入 2024 年之后数据，Fact Checker 必须记录来源更新时间，并在脚注标注“数据截至 YYYY-MM-DD”。
- **模型幻觉**：任何自动生成段落需由 Fact Checker 逐条核对；若无法验证，标记为“暂缓发布”并记录待确认项。
- **协作冲突**：使用分支或文件锁约定（例如在 `docs/07-composition-log.md` 中标明“IX: Editing by Alice 10:00–12:00 UTC”），避免多人同时覆盖草稿。

## 8. 下一步时间线（建议）

- **T+0（当前）**：完成自动草稿刷新并锁定章节分工。
- **T+1 工作日**：Primary Writer 完成 I、IV、VI、VIII 初稿；Automation Specialist 提交 II、III、V、VII 自动草稿+手工补写。
- **T+2 工作日**：Fact Checker 完成全稿核对并更新修订指令；运行一次 pipeline 应用修订。
- **T+3 工作日**：执行 Style Polish，运行 QA 与语言检查，准备交审版。

该策略一经调整须在页首更新日期与负责人，并同步 `docs/07-composition-log.md`。
