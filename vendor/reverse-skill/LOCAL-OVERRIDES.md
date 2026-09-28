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
