---
name: report-authoring
description: >-
  Use when producing any analysis report, design document, architecture/deployment
  write-up, technical assessment, or research conclusion in this repo (触发词：写报告 /
  设计文档 / 分析报告 / 架构文档 / 技术评估 / 调研结论 / report / design doc). Enforces
  this repo's authoring standard: outline-first + conclusion-last structure, tables
  for comparisons, numbered citations with a 参考资料 section, Mermaid-only diagrams
  with the repo's strict format, and the anti-hallucination protocol. Not for STORM's
  own generated wiki articles, code edits, or short terminal replies.
---

# 报告与设计文档写作（report-authoring）

在本仓库生成"给人读的报告/设计文档"时，遵循仓库权威标准并让其切实生效。**动手前先读**
`docs/authoring/report-style-guide.md` 与附录 `docs/authoring/mermaid-style-guide.md`，
然后按下面的要点执行；标准以那两份文档为准，本技能是其执行入口。

## 必须做到（硬性）

1. **先给章节大纲**：正文前输出本报告的章节大纲，再逐节展开。
2. **结论置后**：层层递进，最终结论放最后一节；不要开篇给答案。
3. **层级标题**：使用 `##`、`###`；避免"任务二""某某图"等过程性/非正式表述。
4. **对比用表格**：并列对比（方案、指标、优劣、取舍）一律用 Markdown 表格。
5. **观点有现实锚点**：每个判断都有可查证的现实事件或数据支撑；空泛预测不写。
6. **数字引注 + 参考资料**：正文用 `[1]` 引注，文末设"参考资料"列出完整名称与链接；
   只引真实可访问来源，不编造。
7. **图表一律 Mermaid**：至少包含**架构图**与**部署图**；可选时序图、数据流图。图表
   周围必须有文字解释，把图、设计决策与需求联系起来。
8. **Mermaid 格式**（详见附录，逐条务必满足）：
   - 文本主要用中文；英文补充用"中文术语（English Term）"，括号一律**全角（）**。
   - **严禁英文圆括号 `(` `)`**；外层容器用 `[]`。
   - 换行用 `<br>`；注释 `%%` 独占一行；图例置顶并用 `classDef` 专业配色；流程步骤带序号。
9. **语言风格**：饱满、流畅、通俗；每个观点展开讲透，不干巴罗列。

## 防幻觉自检（交付前必做）

- 不虚构数据、案例、人名、文献、时间、法规；不确定就写"无法确定"，不强答。
- 不做无依据推断，不脑补细节；事实须可查证来源，观点须标注为个人理解。
- 不用"据报道""相关研究显示"等模糊来源；不杜撰文件、条款、标准、论文、统计数字。
- 输出前逐条清除未经证实、无法溯源、主观臆断的内容。

## 复用与校验

- 附录里的架构图、部署图、时序图、数据流图示例均为合规模板，可直接改写复用。
- 提交前可跑 `pytest integrations/claude_code/tests/test_mermaid_style.py`，它会扫描
  `docs/` 的 Mermaid 代码块并拦截英文圆括号与 `\n` 字面量，确保格式落地。
