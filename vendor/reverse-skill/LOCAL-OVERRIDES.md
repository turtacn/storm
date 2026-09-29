# Local overrides (repo-scoped)

These overrides take precedence over upstream defaults **within this repository**.
They add constraints; they never loosen `RULES.md` (authorization/scope still apply).

## Override 1 — No-auth external retrieval (mandatory)

All external information retrieval performed by any skill in this pack — web search,
OSINT, threat-intel lookups, document/page fetching — MUST use **no-authorization**
methods only. Concretely:

- **Prefer** the Claude Code built-ins `WebSearch` / `WebFetch` (no user API key), and
  keyless engines such as **DuckDuckGo** or a self-hosted **SearXNG**.
- **Do NOT** require, prompt for, or depend on API keys / tokens for retrieval, e.g.
  Bing / Google CSE / Serper / You.com / Tavily paid search, or Shodan / VirusTotal /
  Censys / paid X(Twitter) intel APIs.
- If a skill's default path needs an authorized service, **substitute a no-auth
  equivalent** where one exists, otherwise **skip that step and record the gap** in the
  case notes (`work/<case>/…`) rather than blocking on a key.

Skills most affected (use no-auth OSINT / built-in web tools instead of paid APIs):
`skills/threat-intelligence`, `skills/pentest-tools` (incl. `src-hunter` recon),
`skills/threat-hunting`, and any reference that assumes a keyed search/intel provider.

This mirrors the repo-wide policy in
[`../../docs/extensions/no-auth-external-retrieval.md`](../../docs/extensions/no-auth-external-retrieval.md).

## Override 2 — On-demand tool bootstrap stays local

The pack may bootstrap tools on demand. Keep everything within this repo / the current
machine; do not fetch from unpinned external archives. Prefer tools already present
(`skills/tool-index.md`) and no-auth sources.

## Override 3 — 报告产出遵循仓库写作标准

包内任何生成"给人读的报告/文档"的技能——尤其是 `skills/docs-generator`，它会在逆向、
渗透、CTF、安全分析等任务结束时产出正式报告——除遵循自身模板外，其产出**还必须**符合
本仓库的写作标准：`docs/authoring/report-style-guide.md` 及其 Mermaid 附录
`docs/authoring/mermaid-style-guide.md`。要点：章节大纲先行、结论置后、关键对比用表格、
`[n]` 数字引注加文末"参考资料"、**引用自闭环**（`[n]` 引注与跨文档链接处须就地写出被引来源的
关键事实与结论，读者不跳转即可完整理解，跳转仅供核验；不为此刻意限制篇幅——尤其逆向/渗透
报告里的证据、命令、CVE 结论须就地讲清，不能只丢一个跳转）、图表一律 Mermaid（全角括号、
`<br>` 换行、`%%` 注释独占一行、图例置顶配色），并完成防幻觉自检。
