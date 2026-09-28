# 无授权外部检索策略 / No-auth external retrieval policy

**策略**：本仓库内**所有**"从外部获取信息"的能力（web 搜索、OSINT、威胁情报、
抓取网页/文档）都必须使用**无需 API 授权**的方案；不得要求或依赖任何 API key /
token 才能检索。

> Policy: every external information-retrieval path in this repo MUST work with
> **no API authorization**. No search/intel API keys may be required for retrieval.

## 首选的无授权方式 / Preferred no-auth mechanisms

- Claude Code 内置 `WebSearch` / `WebFetch`（走 harness，不用用户 API key）。
- **DuckDuckGo**（keyless）或自建 **SearXNG**。
- 直接对公共端点发 HTTP（无鉴权）。

## 各集成如何满足 / How each integration complies

### STORM 集成
- **检索器默认 `duckduckgo`（无 key）**。见
  `integrations/claude_code/run_storm_claude.py` 的 `--retriever` 默认值与
  `RETRIEVER_ENV`（DuckDuckGo/SearXNG 标记为无需 key）。
- **向量/重排用本地** `SentenceTransformer`（`knowledge_storm/storm_wiki/modules/
  storm_dataclass.py`），无需 embedding API。
- 需要 key 的检索器（bing/you/serper/brave/tavily）保持**可选**，绝不作为默认；
  preflight 会在缺 key 时报错并建议改用 duckduckgo。
- 说明：`ANTHROPIC_API_KEY` 是**语言模型**（大脑）所需，属于"模型"而非"外部信息
  检索"，不在本策略范围内。

### Grilling 套件（grill-with-docs）
- `grilling` 派发的"事实查证"子 agent 使用 Claude Code 内置工具（`WebSearch` /
  `WebFetch` / 文件工具），天然无授权。

### 逆向技能包（vendor/reverse-skill）
- 由 `vendor/reverse-skill/LOCAL-OVERRIDES.md` 强制：包内任何检索一律走无授权方式，
  涉及付费搜索/情报 API 的默认路径需替换为无授权等价物或跳过并记录。

## 校验 / Checks

`integrations/claude_code/tests/test_vendored_skills.py` 断言：STORM 默认检索器为
keyless、no-auth 策略文档与包内 overlay 存在。
