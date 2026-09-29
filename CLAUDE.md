# CLAUDE.md — 项目约定（始终加载）

本仓库为 STORM（`knowledge_storm/`，上游研究代码，保持零改动）加上一层 **Claude Code
集成与扩展**。以下约定对在本仓库内的工作**具有约束力**；详细规范见对应文档。

## 绑定约定

### 1. 报告与设计文档的写作标准（强制）

当你产出**分析报告、设计文档、架构/部署说明、技术评估、调研结论**这类"给人读的文档"
时，**必须**遵循 `docs/authoring/report-style-guide.md` 及其附录
`docs/authoring/mermaid-style-guide.md`，并优先调用 `report-authoring` 技能。要点：
先给章节大纲、结论置后、对比用表格、观点须有现实锚点、`[n]` 数字引注加文末"参考资料"、
**引用自闭环**（`[n]` 引注与跨文档链接处须 in-place 阐述被引内容的关键事实与结论，读者不
跳转即可完整理解，跳转仅供核验；不为此刻意限制篇幅）、图表一律 Mermaid（至少含架构图与
部署图，严禁英文圆括号、换行用 `<br>`、注释 `%%` 独占一行、图例置顶配色）。

> 适用于**新生成的报告/文档**；不适用于 STORM 流水线自动生成的维基式文章、代码改动、
> 以及终端里的简短交互答复。

### 2. 无授权外部检索（强制）

所有"从外部获取信息"（web 搜索、OSINT、抓取）**一律使用无需 API 授权**的方案；细则与
各集成的落地见 `docs/extensions/no-auth-external-retrieval.md`。

### 3. 防幻觉与核验（强制）

产出事实性内容时：不虚构数据/案例/人名/文献/时间/法规；不确定就答"无法确定"，不强答；
不做无依据推断；事实须可查证来源、观点须标注为个人理解。完整清单见写作标准文档的
"防幻觉与核验强制要求"一节。

**结论闭环（与上不矛盾）**：防幻觉禁止**编造**；但交付级报告**不得**把"无法确定/待实测/待证"
当悬留问题堆着——须去核实并推进到闭环：① 已核验事实；② 有依据的工程判断 + 可证伪门（预测须
标注）；③ 确定的"公开不可得"判定 + 处理。难定论的高价值项，**启动多个独立资深 reviewer 对拍**
（配置同主 agent）再核验后采纳。细则见写作标准的"结论闭环（不留悬留存疑）"一节。

## 目录导航

| 位置 | 内容 |
|---|---|
| `knowledge_storm/` | STORM 内核（上游，未改动） |
| `integrations/claude_code/` | STORM×Claude Code 运行器、preflight、测试 |
| `.claude/skills/` | 本仓库技能：`storm-research`、`report-authoring`、`competitive-analysis`，以及 vendored 的 `grill-with-docs`/`grilling`/`domain-modeling` |
| `.claude/commands/` | 斜杠命令：`/storm`、`/compare` |
| `vendor/reverse-skill/` | vendored 逆向/安全技能路由包（源码自包含，见其 `VENDORED-INTO-STORM.md`） |
| `docs/authoring/` | 报告写作标准与 Mermaid 格式规范 |
| `docs/extensions/` | 集成设计、能力边界、无授权检索策略 |
| `docs/harness-sop/` | 竞品对标分析 SOP 文档与案例（`examples/`） |

## 测试

```bash
pytest integrations/claude_code/tests -q
```
