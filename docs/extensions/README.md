# STORM × Claude Code CLI 集成 / Extensions

本目录记录 STORM 与 **Claude Code CLI** 的集成扩展。集成不修改 STORM 核心
（`knowledge_storm/`），而是以"附加层"的方式提供：让 Claude Code 去**驱动** STORM，
并用 **Claude 模型（经 LiteLLM）**作为 STORM 的大脑。

> This directory documents an *additive* integration between STORM and the
> **Claude Code CLI**. It does not modify the STORM core; it lets Claude Code drive
> STORM, with Claude models (via LiteLLM) as the backend.

## 集成的两半 / The two halves

| 方案 | 含义 | 落地文件 |
|---|---|---|
| **方案一** | Claude Code 把 STORM 当工具去编排（Skill / 斜杠命令 / Bash） | `.claude/skills/storm-research/SKILL.md`、`.claude/commands/storm.md` |
| **方案四** | STORM 内部用 `LitellmModel` 直连 Claude（当前模型、非交互、机器可读输出） | `integrations/claude_code/run_storm_claude.py` |
| 辅助 | 运行前环境/密钥自检 | `integrations/claude_code/preflight.py` |

（编号沿用最初分析里的四个集成方向，见 [capability-boundaries.md](capability-boundaries.md)。）

## 快速开始 / Quickstart

```bash
# 0) 一次性：装依赖（较大，含 torch/sentence-transformers）
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

# 1) 配置密钥：复制模板到仓库根目录并填入 ANTHROPIC_API_KEY
cp integrations/claude_code/secrets.toml.example secrets.toml   # 然后编辑

# 2) 自检
python3 integrations/claude_code/preflight.py --retriever duckduckgo

# 3) 直接跑（默认 DuckDuckGo，无需搜索 Key）
python3 integrations/claude_code/run_storm_claude.py \
  --topic "Retrieval-augmented generation" --print-summary
```

在 Claude Code 里，直接说"用 STORM 写一篇关于 X 的调研"即可触发
`storm-research` 技能，或使用斜杠命令 `/storm <topic>`。技能会自动完成
自检 → 后台运行 → 轮询产物 → 汇总呈现。

## 产物 / Outputs

结果写到 `./results/claude_code/<topic_slug>/`，其中：

- `storm_gen_article_polished.txt` — 最终文章（首选）
- `storm_gen_article.txt` — 草稿文章
- `storm_gen_outline.txt` / `direct_gen_outline.txt` — 大纲
- `url_to_info.json` — 引用来源
- `claude_code_summary.json` — 机器可读运行摘要（供 Claude Code 解析）

`results/` 已在 `.gitignore` 中，不会误提交。

## 另一个扩展：Grilling 套件 / Grilling suite

本目录还内置了一个**自包含**的 `grill-with-docs` 套件（vendored 自
`mattpocock/skills`，MIT）：一个单会话"拷问式"设计澄清技能，边谈边把术语写进
`CONTEXT.md`、把关键决策写成 `docs/adr/` 的 ADR。用户显式触发：`/grill-with-docs`。
它与 STORM 无关，仅同处本分支。详见 [grilling-suite.md](grilling-suite.md) 与
[`.claude/skills/VENDOR-NOTICE.md`](../../.claude/skills/VENDOR-NOTICE.md)。

> 注意：它是**面向你本人的面试式澄清**，不是"多 reviewer agent 并行审查"。

## 更多 / More

- [claude-code-integration.md](claude-code-integration.md) — STORM 集成的架构、
  数据流、配置、用法、测试的完整说明。
- [capability-boundaries.md](capability-boundaries.md) — 能力边界、"集成"的
  三种含义、为何不推荐把 `claude -p` 当后端，以及替代方案。
- [grilling-suite.md](grilling-suite.md) — vendored `grill-with-docs` 套件的
  说明、用法、自包含校验与许可。
