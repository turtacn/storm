# 能力边界、集成语义与替代方案

本文沉淀集成前的分析结论：STORM 能做什么/不能做什么、"与 Claude Code 集成"的
三种不同含义、为何本集成选择方案一+方案四，以及有哪些替代方案。

## 1. STORM 是什么

Stanford OVAL 的 STORM（`knowledge-storm`，MIT）是一个基于 `dspy 2.4.9 + litellm`
的**批处理式研究流水线**：输入主题 → 自动上网检索、多视角提问 → 生成带引用的
维基百科式长文。两个引擎：

- **STORM Wiki**（批处理）：`STORMWikiRunner.run()`，四阶段——知识策展 → 大纲 →
  正文 → 润色。
- **Co-STORM**（交互式）：`CoStormRunner.warm_start()/step()/generate_report()`，
  人在环 + 动态"思维导图"。

它是一个 **Python 库**，没有打包 CLI，没有服务/守护进程；对外调用要么跑
`examples/` 脚本，要么 `import knowledge_storm`。

## 2. 能力边界

**擅长**：把一个主题自动变成结构化、带引用的维基式长文；多视角提问带来广度；
分阶段选模型省成本；四阶段可断点续跑。

**硬性依赖 / 前提**
- 必须有**检索后端**（除 DuckDuckGo 无 Key、SearXNG 可自建外都要 Key）+ **LLM Key**。
- 基础 STORM Wiki 用**本地** `SentenceTransformer("paraphrase-MiniLM-L6-v2")` 做
  片段重排（`storm_wiki/modules/storm_dataclass.py`）——首次运行会从 HuggingFace
  下载模型。
- **Co-STORM / VectorRM** 额外需要 embedding：设 `ENCODER_API_TYPE`(openai/azure) +
  对应 Key（`encoder.py`）。
- Python 3.10/3.11；`dspy_ai==2.4.9` 为**死锁版本**，是最大的工程脆弱点，易与现代
  生态冲突。

**质量边界**：作者自述"产出非可直接发表的成品，适合写作前草稿"；引用可能错配；
默认只有维基式中立长文一种形态；偏英文；输出质量受搜索质量限制。

**运行特性**：单篇**分钟级**、并发打 LLM，易撞速率限制（用 `--max-thread-num` 降并发）。

**维护活跃度**：真正改代码的最后提交约在 2025-04，2025-09 仅放宽 requirements 版本；
可视为**成熟但低维护**。

## 3. "与 Claude Code CLI 集成"的三种含义

| 含义 | 说明 | 本集成的取舍 |
|---|---|---|
| **A. Claude Code 编排 STORM** | 把 STORM 当工具，由 Claude Code 发起/读结果 | ✅ 采用（方案一：Skill + 命令） |
| **B. STORM 用 Claude Code/订阅当后端** | 让 STORM 走 `claude -p` 或订阅额度 | ❌ 不采用（见下节） |
| **C. STORM 用 Claude(API) 当大脑** | `LitellmModel(model="anthropic/claude-*")` | ✅ 采用（方案四） |

### 关键：认证模型不互通
Claude Code 用**订阅（Pro/Max 的 OAuth）或 API Key**；STORM 库这条路（litellm/
anthropic SDK）只认**环境变量里的真实 API Key**。二者不共享凭证——STORM 库**无法
自动蹭** Claude Code 的订阅额度。唯一的桥是 shell 调用 `claude` 二进制（即含义 B）。

## 4. 为何不把 `claude -p` 当 STORM 后端（方案三/含义 B）

技术上可行：自定义一个 LM 类（实现 `__call__(prompt)->list[str]`，并补上
`.kwargs/.history/get_usage_and_reset()`，接口见 `knowledge_storm/interface.py` 的
`LMConfigs`），在其中 `subprocess` 调 `claude -p ... --output-format json`。但**不划算**：

1. STORM 每篇发几十上百次调用且多线程并发，等于反复并发拉起多个 `claude` agent
   进程，又慢又重；
2. `claude -p` 不干净地暴露 `temperature/top_p/n` 等 STORM 依赖的采样参数；
3. 每次都套一层"写代码用"的 agent 系统提示与工具循环，污染输出、放大 token；
4. Claude Code 本质是 agent，不是批量 completion API。

结论：当实验可以，别上生产。故本集成走"Claude Code 编排 + litellm 直连 Claude API"。

## 5. 替代方案

**若目标只是"研究某主题 → 带引用报告"，且你已在用 Claude Code：**
- **Claude Code 本身**：`WebSearch` + `WebFetch` + 并行子 agent（不同视角）+ 研究
  Skill + 输出到 **Artifact**。几乎复刻 STORM 价值，零额外依赖，原生贴合当前工作流；
  代价是"多视角提问"的方法论需自行在 prompt/skill 里设计。
- **Claude Agent SDK**（Python/TS）：想要 STORM 式结构化流水线但**可维护**、原生对接
  Claude/工具/MCP/子 agent/流式——比抱着 dspy 2.4.9 更面向未来。

**现成开源 "deep research" 项目**
- **GPT-Researcher**：最流行、更新勤、自带 MCP server，通常更开箱即用。
- **LangChain Open Deep Research / Local Deep Researcher（Ollama）**：在 LangGraph 生态里。
- 各种 open-deep-research 轻量克隆（HuggingFace smolagents 等）。

**托管产品（不可集成，仅对比）**：OpenAI Deep Research、Perplexity、Google Deep
Research、以及 Anthropic 自家研究功能。

> 外部项目的活跃度/接口以你实际拉取时为准。

## 6. 何时用哪个

- 想保留 STORM/Co-STORM 特定方法论、要维基式带引用长文、又想少折腾 → 用本集成
  （方案一驱动 + 方案四供能）。
- 只想要"研究→带引用报告"，更看重可维护性与原生集成 → 直接用 Claude Code +
  子 agent + WebSearch + Artifact，或写个小的 Claude Agent SDK agent；要现成工具就上
  GPT-Researcher。
- 纯为省订阅额度把 `claude -p` 当后端 → 不建议。
