---
name: storm-research
description: >-
  Use when the user wants to turn a TOPIC into a long, citation-backed,
  Wikipedia-style article/report by running this repo's STORM pipeline with Claude
  models. Drives integrations/claude_code/run_storm_claude.py (LiteLLM -> Claude)
  as a background job and presents the finished article. Triggers include: "用 STORM
  写一篇关于…", "research this topic into a cited article", "生成带引用的维基式长文/
  调研报告", "run storm on <topic>", "storm 调研 <主题>". Not for quick one-paragraph
  answers or for editing an existing article.
---

# STORM research (Claude-backed)

Run the STORM knowledge-curation pipeline to produce a cited, Wikipedia-style
article about a topic, using Claude models via LiteLLM. STORM does its own web
research; you (Claude Code) orchestrate the run and present the result.

Repo-root-relative paths are used below. Confirm you are at the repo root first.

## 1. Preflight (always do this first)

Pick the retriever (default `duckduckgo`, needs no key). Then:

```bash
python3 integrations/claude_code/preflight.py --retriever duckduckgo
```

Parse the JSON. Act on the first failing check:

- **`import:knowledge_storm` false** — deps aren't installed. Tell the user this
  needs a one-time environment setup that is **large and slow** (pulls torch via
  sentence-transformers) and ask before proceeding. On approval:
  ```bash
  # 本地绿色安装：项目内 venv，无需 sudo，不改系统
  python3 -m venv .venv && . .venv/bin/activate \
    && pip install -r requirements.txt -r integrations/claude_code/requirements-extra.txt
  ```
  After that, run STORM with `.venv/bin/python` instead of `python3`. 模型用**与主 agent 一致**的
  配置（例如 `STORM_CLAUDE_STRONG_MODEL=anthropic/claude-fable-5`、`STORM_CLAUDE_FAST_MODEL=...`）；
  检索保持无授权（DuckDuckGo）。
- **`ANTHROPIC_API_KEY` missing** — ask the user to export it or add it to
  `secrets.toml` (copy `integrations/claude_code/secrets.toml.example`). This is an
  **Anthropic API key**, not their Claude Code subscription — the two are separate.
- **`retriever:<name>` missing key** — set that key, or fall back to
  `--retriever duckduckgo`.

Do not start a run until preflight is `ok: true` (or the user explicitly says to).

## 2. Launch the run in the background

STORM takes **minutes** (many parallel LLM + search calls), so never run it in the
foreground. Use a background shell:

```bash
python3 integrations/claude_code/run_storm_claude.py \
  --topic "<TOPIC>" \
  --retriever duckduckgo \
  --output-dir ./results/claude_code \
  --max-thread-num 3 \
  --print-summary
```

Notes:
- Use `.venv/bin/python` if you created a venv in step 1.
- Defaults: strong model for outline/article/polish, fast model for the research
  conversation. Override with `--strong-model` / `--fast-model` or the
  `STORM_CLAUDE_STRONG_MODEL` / `STORM_CLAUDE_FAST_MODEL` env vars.
- Stage flags (`--do-research`, `--do-generate-outline`, `--do-generate-article`,
  `--do-polish-article`) let you re-run parts; with none given, all four run.

## 3. Wait for completion, then read the summary

The run writes a machine-readable summary when it finishes. Poll for it (the topic
becomes a slug: spaces and `/` -> `_`, truncated to 125 chars):

```bash
cat "./results/claude_code/<TOPIC_SLUG>/claude_code_summary.json"
```

The JSON contains: `ok`, `article_path`, `files`, `num_references`, `stages_run`,
`models`, `retriever`, `elapsed_seconds`, `token_usage`. If `ok` is false, read
`error`/`type` and act on it (see Troubleshooting).

## 4. Present the result

Read `article_path` (the polished article if present, else the draft) and give the
user:
- a 2-4 sentence digest of what was produced (length, section count, #references);
- the path to the full article and reference list (`files.url_to_info`);
- an offer to publish it as an **Artifact** for easy reading/sharing.

Do not paste the entire article into chat unless asked; summarize and point to the
file, or publish the Artifact.

## Troubleshooting

- **Rate limits / "Exceed rate limit"** — lower `--max-thread-num` (try 1-2).
- **Thin or low-quality article** — the default DuckDuckGo search is weakest;
  switch to `--retriever tavily` (or `bing`/`serper`) with the matching key.
- **Model id rejected (404 / not found)** — set `--strong-model` / `--fast-model`
  to ids your Anthropic account supports, e.g.
  `anthropic/claude-3-5-sonnet-latest` and `anthropic/claude-3-5-haiku-latest`.
- **Only need part of the pipeline** — re-run with just the stage flags you want;
  earlier stages are loaded from the output dir if present.

## What this is NOT

This runs STORM *using Claude as the model backend via the Anthropic API*. It does
**not** route STORM through your Claude Code subscription, and it is a batch tool,
not an interactive chat. See `docs/extensions/` for the full design, capability
boundaries, and alternatives.
