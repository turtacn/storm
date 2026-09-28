---
name: competitive-analysis
description: >-
  Use for a comprehensive product / technology / feature benchmarking analysis that
  ends in a decision-ready report. Orchestrates this repo's skills (grilling ->
  storm-research -> report-authoring) to answer the paradigm: 结合学术界在某方向 XXX 的
  最新研究热点，针对产品 YYY 对标产品 ZZZ 做差距分析、行动 roadmap、最优价值 MVP 架构
  设计，以及 MVP 价值兑现（产品 FAB、客户语言的价值、控标经典案例）. Triggers: 竞品分析 /
  产品对标 / 差距分析 / 技术对标 / 对标报告 / competitive analysis / benchmark.
---

# 竞品对标分析 SOP（competitive-analysis）

把本仓库的技能族编排为一条标准作业流程，产出一份**决策级**的产品/技术/特性对标分析报告。
输入三要素：**XXX**（技术或产品方向）、**YYY**（本方产品）、**ZZZ**（对标产品）；可选：目标
客户、行业、招投标背景。产物是一份严格符合本仓库写作标准的报告。

全流程遵守两条硬规矩：**检索一律无授权**（见 `docs/extensions/no-auth-external-retrieval.md`）；
**严禁虚构**（见写作标准的防幻觉一节），尤其"控标经典案例"只用可核验的真实信息，查不到就
写"无法确定"。

## 阶段流程

### 阶段一 · 澄清与范围界定（用 `grilling`）
调用 `grilling` 技能，把问题打磨清楚再动手：XXX 的确切边界与评价维度、YYY 与 ZZZ 的版本/
形态、对标目的、目标客户与其痛点、招投标或采购背景。若在仓库内工作，用 `domain-modeling`
把术语与关键判断落成 `CONTEXT.md` / ADR。**产出**：一页范围界定说明（含评价维度清单）。

### 阶段二 · 学术热点与情报调研（用 `storm-research` + 无授权检索）
用 `storm-research`（其后端为 `run_storm_claude.py`，默认 DuckDuckGo 无授权检索）就"XXX 方向
最新研究热点与技术趋势"生成带引用的研究底稿。可并行派发只读子代理（内置 `WebSearch` /
`WebFetch`，无授权）分别收集：学术热点、ZZZ 的公开技术情报、YYY 现有能力。**产出**：带
`[n]` 引用的研究与情报底稿。

> 说明：学术方向如需更聚焦，可加检索 arXiv 等公开来源；所有来源必须真实可核验。ZZZ 的技术
> 剖析只使用公开信息，不做未授权的逆向或抓取。

### 阶段三 · 对标差距分析（用 `report-authoring`，表格化）
围绕阶段一的评价维度，逐维给出 YYY 与 ZZZ 的对比，用表格承载；每条差距都要有阶段二的
现实证据支撑，并说明它为何重要（与学术热点/客户痛点挂钩）。**产出**：差距分析表 + 解读。

### 阶段四 · 行动 Roadmap
把差距转成分期（近期/中期/远期）的行动项，按"价值×可行性"排序，每项对应到具体差距与预期
收益，用时间线图（Mermaid，合规）可视化。**产出**：Roadmap 表 + 时间线图。

### 阶段五 · 最优价值 MVP 架构设计
从 Roadmap 中选出"价值最高、可行性最好"的最小切片，给出 MVP 架构设计：用 Mermaid 架构图与
部署图（合规）呈现模块层次、依赖与运行时关系，并论证其如何针对性地补齐差距、吸收学术最佳
实践。**产出**：MVP 架构图 + 部署图 + 设计论证。

### 阶段六 · MVP 价值兑现
- **产品 FAB**：用表格给出 特性（Feature）→ 优势（Advantage）→ 利益（Benefit）的映射。
- **客户语言的价值**：把技术特性翻译成客户能听懂的业务结果（效率、成本、风险、合规、收入），
  避免技术黑话。
- **控标经典案例**：给出可作为招投标差异化技术门槛的能力点；**只引用真实、可核验的案例**，
  不得杜撰客户名、项目、金额或结果；无可核验案例时明确写"无法确定"。

### 阶段七 · 成文（用 `report-authoring`）
按 `docs/authoring/report-style-guide.md` 与附录 `mermaid-style-guide.md` 组装最终报告：
先给章节大纲、结论置后、关键对比用表格、`[n]` 数字引注加文末"参考资料"、所有图表为 Mermaid
且符合格式（全角括号、`<br>`、`%%` 独占行、图例置顶配色）。交付前完成防幻觉自检。可发布为
Artifact 便于分享。

## 报告结构与落盘位置

严格采用 `docs/harness-sop/report-outline.md` 的章节骨架（与上面的问题范式一一对应），它
自带各章要点与合规的 Mermaid/表格占位，可直接改写复用。本 SOP 的完整说明见
`docs/harness-sop/README.md`；每次生成的案例报告统一落到 `docs/harness-sop/examples/`
（按 `对标方向-YYY-vs-ZZZ-日期` 命名）。

## 交付前自检（必过）
- [ ] 章节大纲先行、结论置后；关键对比均为表格。
- [ ] 每条判断有真实可核验来源；`[n]` 引注 + 文末"参考资料"齐全。
- [ ] 含 MVP 架构图与部署图，全部 Mermaid 且格式合规。
- [ ] 控标案例等敏感内容无虚构，查不到即写"无法确定"。
- [ ] 检索全程无授权；未使用任何需 API 密钥的搜索/情报服务。
