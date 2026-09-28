# Grilling suite（`grill-with-docs`）—— 自包含 vendored 技能

本仓库把 `grill-with-docs` 及其依赖链**自包含**地内置在 `.claude/skills/` 下，
无需任何外部安装脚本 / archive / 全局安装即可在本项目里使用。

## 这是什么

`grill-with-docs` 是一个**单会话、有状态的"拷问式"设计澄清**技能：它像面试一样
一轮轮追问你的计划/设计，直到你和 agent 对它达成同一理解，并在过程中**边谈边落盘**：

- 谈清的**术语** → 写进根目录 `CONTEXT.md` 术语表（术语一确定就即时写入，不攒到最后）；
- 满足"难以逆转 + 无背景会困惑 + 真实取舍"三条的**决策** → 写成 `docs/adr/` 下的 ADR；
- 其余内容留在对话里。

它由三个 vendored 技能组成（`.claude/skills/`）：

| 技能 | 作用 |
|---|---|
| `grill-with-docs/` | 入口，一行委派：调用下面两个技能 |
| `grilling/` | 拷问/面试原语：把设计拆成决策树，按"轮"提问，每题给推荐答案，等你回答再下一轮 |
| `domain-modeling/` | 把术语表（`CONTEXT.md`）和 ADR 落盘；含 `ADR-FORMAT.md`、`CONTEXT-FORMAT.md` |

## 重要：它不是"多 reviewer agent 扇出"

先前设想的是"把问题 grill 给多个 reviewer 子 agent 并行审查"。**`grill-with-docs`
不是那个东西**——它是**单 agent、面向你本人**的面试式澄清（决策都交给你拍板）。
唯一的并行是：`grilling` 会派**事实查证**子 agent 去读文件系统/工具找事实（而不是让你
回答能自己查到的东西），但这不是多 reviewer 评审。若你要的是多评审并行对抗，那是另一个
技能（可另建 `grill-reviewers`），与本 vendored 套件正交。

## 如何用

在仓库根目录的 Claude Code 里，用户显式触发（技能带 `disable-model-invocation: true`，
不会自动触发）：

```
/grill-with-docs
```

然后描述你要澄清的变更/设计即可。产物：

- `CONTEXT.md`（根目录术语表，懒创建）
- `docs/adr/NNNN-*.md`（有合格决策时才产生；多数会话可能一个都不产生，属正常）

会话结束后，若要进一步产出规格，可把同一对话喂给上游的 `to-spec`（本仓库未 vendored，
见下）。

## 自包含与校验

- 委派链完整内置：`grill-with-docs → grilling / domain-modeling`；`domain-modeling`
  引用的 `ADR-FORMAT.md`、`CONTEXT-FORMAT.md` 均在同目录。
- 无外部硬依赖（`grilling` 派发的是 Claude Code 内置的通用子 agent）。
- 自包含不变量由测试守护：
  `integrations/claude_code/tests/test_vendored_skills.py`。

## 来源与许可

- 来源：https://github.com/mattpocock/skills，commit `c55ee46`。
- 许可：MIT（Copyright (c) 2026 Matt Pocock）。完整声明与刷新方式见
  [`.claude/skills/VENDOR-NOTICE.md`](../../.claude/skills/VENDOR-NOTICE.md)。

## 未 vendored（有意省略）

- 各技能上游的 `agents/openai.yaml`：那是 OpenAI/Codex 的配置，与 Claude Code 无关。
- 下游链 `to-spec` → `to-tickets` → `implement` → `code-review`：本次未内置；
  `grill-with-docs` 不依赖它们也能独立工作。需要时可同样方式再 vendored。

## 与 STORM 集成的关系

两者相互独立，仅因你的要求同处 `feat/claude-code-integration` 分支：STORM 集成解决
"研究→带引用长文"，本套件解决"设计前把话说清、把术语与关键决策落盘"。
