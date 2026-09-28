#!/usr/bin/env python3
"""Non-interactive STORM Wiki runner wired to Claude models through LiteLLM.

This is the "方案四" half of the Claude Code CLI integration. Compared with
``examples/storm_examples/run_storm_wiki_claude.py`` it is built to be driven by
an agent / background job rather than a human at a prompt:

* **Non-interactive** -- the topic comes from ``--topic`` (no ``input()`` call),
  so the Claude Code ``storm-research`` skill can launch it unattended.
* **Supported model path** -- uses :class:`knowledge_storm.lm.LitellmModel`
  (recommended since ``knowledge-storm`` v1.1.0) instead of the deprecated
  ``ClaudeModel``, so current Claude model ids work by just changing a string.
* **Zero-key friendly** -- defaults to the keyless DuckDuckGo retriever, so a run
  needs only ``ANTHROPIC_API_KEY``; other retrievers are opt-in via ``--retriever``.
* **Machine-readable** -- writes ``<output_dir>/<topic>/claude_code_summary.json``
  and can echo that JSON to stdout (``--print-summary``) for the agent to parse.

Heavy third-party imports (``knowledge_storm``, ``litellm`` ...) are performed
lazily *inside* functions, so this module can be imported and unit-tested without
the STORM dependency stack installed.

Environment variables
---------------------
ANTHROPIC_API_KEY
    Required. Credentials for the Claude models (this is an Anthropic API key --
    it is *not* your Claude Code subscription; see docs/extensions).
STORM_CLAUDE_STRONG_MODEL / STORM_CLAUDE_FAST_MODEL
    Optional. Override the default model ids without editing this file. For config
    consistency, set these to the SAME model the main Claude Code agent uses
    (e.g. anthropic/claude-fable-5) so STORM's backend matches the main agent.
<RETRIEVER>_API_KEY
    Only required for non-DuckDuckGo retrievers (see ``RETRIEVER_ENV``).

Keys may also be supplied via a ``secrets.toml`` file (``--secrets``), which is
loaded into the environment before the run.
"""

import argparse
import json
import os
import sys
import time

# Default Claude model ids (LiteLLM "anthropic/..." routing). These are the
# current generation as of writing; override with --strong-model/--fast-model or
# the STORM_CLAUDE_* env vars if your account or litellm version expects other
# ids (e.g. "anthropic/claude-3-5-sonnet-latest").
FALLBACK_STRONG_MODEL = "anthropic/claude-sonnet-4-5"
FALLBACK_FAST_MODEL = "anthropic/claude-haiku-4-5"

# Retriever -> environment variable holding its API key. ``None`` means the
# retriever needs no key (keyless, or self-hosted / optional key).
RETRIEVER_ENV = {
    "duckduckgo": None,
    "searxng": None,
    "bing": "BING_SEARCH_API_KEY",
    "you": "YDC_API_KEY",
    "serper": "SERPER_API_KEY",
    "brave": "BRAVE_API_KEY",
    "tavily": "TAVILY_API_KEY",
}

# Output files STORM may produce, in a stable key -> filename mapping.
OUTPUT_FILES = {
    "conversation_log": "conversation_log.json",
    "raw_search_results": "raw_search_results.json",
    "direct_gen_outline": "direct_gen_outline.txt",
    "storm_gen_outline": "storm_gen_outline.txt",
    "url_to_info": "url_to_info.json",
    "draft_article": "storm_gen_article.txt",
    "polished_article": "storm_gen_article_polished.txt",
    "run_config": "run_config.json",
    "llm_call_history": "llm_call_history.jsonl",
}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser. Pure -- no side effects, safe to call in tests."""
    p = argparse.ArgumentParser(
        prog="run_storm_claude",
        description="Run the STORM Wiki pipeline with Claude models (LiteLLM).",
    )
    p.add_argument("--topic", required=True, help="Topic to research and write about.")
    p.add_argument(
        "--output-dir",
        default="./results/claude_code",
        help="Directory to store outputs (a per-topic subdirectory is created).",
    )
    p.add_argument(
        "--retriever",
        default="duckduckgo",
        choices=sorted(RETRIEVER_ENV.keys()),
        help="Search backend. 'duckduckgo' needs no API key (default).",
    )
    # Models.
    p.add_argument(
        "--strong-model",
        default=os.getenv("STORM_CLAUDE_STRONG_MODEL", FALLBACK_STRONG_MODEL),
        help="Model for outline/article/polish (quality-critical stages).",
    )
    p.add_argument(
        "--fast-model",
        default=os.getenv("STORM_CLAUDE_FAST_MODEL", FALLBACK_FAST_MODEL),
        help="Model for conversation simulation / question asking (frequent, cheap).",
    )
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--top-p", type=float, default=0.9)
    # Per-slot max tokens (mirrors the defaults in the official Claude example).
    p.add_argument("--conv-max-tokens", type=int, default=500)
    p.add_argument("--question-max-tokens", type=int, default=500)
    p.add_argument("--outline-max-tokens", type=int, default=400)
    p.add_argument("--article-max-tokens", type=int, default=700)
    p.add_argument("--polish-max-tokens", type=int, default=4000)
    # Pipeline hyper-parameters.
    p.add_argument("--max-conv-turn", type=int, default=3)
    p.add_argument("--max-perspective", type=int, default=3)
    p.add_argument("--max-search-queries-per-turn", type=int, default=3)
    p.add_argument("--search-top-k", type=int, default=3)
    p.add_argument("--retrieve-top-k", type=int, default=3)
    p.add_argument(
        "--max-thread-num",
        type=int,
        default=3,
        help="Parallel LM/search threads. Lower it if you hit rate limits.",
    )
    # Stages. If none are given, all four run.
    p.add_argument("--do-research", action="store_true")
    p.add_argument("--do-generate-outline", action="store_true")
    p.add_argument("--do-generate-article", action="store_true")
    p.add_argument("--do-polish-article", action="store_true")
    p.add_argument("--remove-duplicate", action="store_true")
    # I/O.
    p.add_argument(
        "--secrets",
        default="secrets.toml",
        help="Optional TOML file of API keys, loaded into the environment.",
    )
    p.add_argument(
        "--print-summary",
        action="store_true",
        help="Print the machine-readable JSON summary to stdout on success.",
    )
    return p


def resolve_stages(args) -> dict:
    """Map stage flags to ``runner.run`` kwargs; default to all stages on."""
    flags = {
        "do_research": bool(args.do_research),
        "do_generate_outline": bool(args.do_generate_outline),
        "do_generate_article": bool(args.do_generate_article),
        "do_polish_article": bool(args.do_polish_article),
    }
    if not any(flags.values()):
        return {key: True for key in flags}
    return flags


def resolve_model_plan(args) -> dict:
    """Assign a model + token budget to each STORM LM slot. Pure."""
    fast = args.fast_model
    strong = args.strong_model
    return {
        "conv_simulator_lm": {"model": fast, "max_tokens": args.conv_max_tokens},
        "question_asker_lm": {"model": fast, "max_tokens": args.question_max_tokens},
        "outline_gen_lm": {"model": strong, "max_tokens": args.outline_max_tokens},
        "article_gen_lm": {"model": strong, "max_tokens": args.article_max_tokens},
        "article_polish_lm": {"model": strong, "max_tokens": args.polish_max_tokens},
    }


def missing_retriever_key(retriever: str):
    """Return the name of the required-but-missing key env var, or ``None``."""
    env_var = RETRIEVER_ENV.get(retriever)
    if env_var and not os.getenv(env_var):
        return env_var
    return None


def build_lm_configs(plan: dict, claude_kwargs: dict):
    """Instantiate a ``STORMWikiLMConfigs`` from a model plan. Lazy imports."""
    from knowledge_storm import STORMWikiLMConfigs
    from knowledge_storm.lm import LitellmModel

    lm_configs = STORMWikiLMConfigs()
    setters = {
        "conv_simulator_lm": lm_configs.set_conv_simulator_lm,
        "question_asker_lm": lm_configs.set_question_asker_lm,
        "outline_gen_lm": lm_configs.set_outline_gen_lm,
        "article_gen_lm": lm_configs.set_article_gen_lm,
        "article_polish_lm": lm_configs.set_article_polish_lm,
    }
    for slot, spec in plan.items():
        model = LitellmModel(
            model=spec["model"], max_tokens=spec["max_tokens"], **claude_kwargs
        )
        setters[slot](model)
    return lm_configs


def build_retriever(args):
    """Instantiate the selected retrieval module. Lazy imports."""
    name = args.retriever
    k = args.search_top_k
    if name == "duckduckgo":
        from knowledge_storm.rm import DuckDuckGoSearchRM

        return DuckDuckGoSearchRM(k=k, safe_search="On", region="us-en")
    if name == "bing":
        from knowledge_storm.rm import BingSearch

        return BingSearch(bing_search_api_key=os.getenv("BING_SEARCH_API_KEY"), k=k)
    if name == "you":
        from knowledge_storm.rm import YouRM

        return YouRM(ydc_api_key=os.getenv("YDC_API_KEY"), k=k)
    if name == "serper":
        from knowledge_storm.rm import SerperRM

        return SerperRM(
            serper_search_api_key=os.getenv("SERPER_API_KEY"),
            query_params={"autocorrect": True, "num": 10, "page": 1},
        )
    if name == "brave":
        from knowledge_storm.rm import BraveRM

        return BraveRM(brave_search_api_key=os.getenv("BRAVE_API_KEY"), k=k)
    if name == "tavily":
        from knowledge_storm.rm import TavilySearchRM

        return TavilySearchRM(
            tavily_search_api_key=os.getenv("TAVILY_API_KEY"),
            k=k,
            include_raw_content=True,
        )
    if name == "searxng":
        from knowledge_storm.rm import SearXNG

        return SearXNG(searxng_api_key=os.getenv("SEARXNG_API_KEY"), k=k)
    raise ValueError(f"Unsupported retriever: {name!r}")


def _count_references(url_to_info_path: str):
    """Best-effort count of cited references from url_to_info.json."""
    try:
        with open(url_to_info_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if isinstance(data, dict):
        for key in ("url_to_unified_index", "url_to_info"):
            if isinstance(data.get(key), dict):
                return len(data[key])
        return len(data)
    if isinstance(data, list):
        return len(data)
    return None


def build_summary(runner, args, plan: dict, stages: dict, elapsed: float) -> dict:
    """Assemble the machine-readable run summary from the finished runner."""
    out_dir = getattr(runner, "article_output_dir", None) or os.path.join(
        args.output_dir, _slugify_topic(args.topic)
    )
    present = {}
    for key, fname in OUTPUT_FILES.items():
        path = os.path.join(out_dir, fname)
        if os.path.exists(path):
            present[key] = path

    num_refs = None
    if "url_to_info" in present:
        num_refs = _count_references(present["url_to_info"])

    article_path = present.get("polished_article") or present.get("draft_article")

    return {
        "ok": True,
        "topic": args.topic,
        "output_dir": out_dir,
        "article_path": article_path,
        "files": present,
        "num_references": num_refs,
        "stages_run": [name for name, on in stages.items() if on],
        "models": {slot: spec["model"] for slot, spec in plan.items()},
        "retriever": args.retriever,
        "elapsed_seconds": round(elapsed, 2),
        "token_usage": getattr(runner, "lm_cost", {}),
        "rm_usage": getattr(runner, "rm_cost", {}),
        "time_per_stage": getattr(runner, "time", {}),
    }


def _slugify_topic(topic: str, max_length: int = 125) -> str:
    """Mirror STORM's directory-naming convention for fallback path building."""
    slug = topic.replace(" ", "_").replace("/", "_")
    return slug[:max_length]


def run_pipeline(args) -> dict:
    """Configure and run STORM, returning the run summary. Lazy imports."""
    from knowledge_storm import STORMWikiRunner, STORMWikiRunnerArguments

    claude_kwargs = {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "temperature": args.temperature,
        "top_p": args.top_p,
    }
    plan = resolve_model_plan(args)
    lm_configs = build_lm_configs(plan, claude_kwargs)
    engine_args = STORMWikiRunnerArguments(
        output_dir=args.output_dir,
        max_conv_turn=args.max_conv_turn,
        max_perspective=args.max_perspective,
        max_search_queries_per_turn=args.max_search_queries_per_turn,
        search_top_k=args.search_top_k,
        retrieve_top_k=args.retrieve_top_k,
        max_thread_num=args.max_thread_num,
    )
    rm = build_retriever(args)
    runner = STORMWikiRunner(engine_args, lm_configs, rm)

    stages = resolve_stages(args)
    start = time.time()
    runner.run(topic=args.topic, remove_duplicate=args.remove_duplicate, **stages)
    runner.post_run()
    elapsed = time.time() - start
    return build_summary(runner, args, plan, stages, elapsed)


def _fail(payload: dict, code: int) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return code


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    # Load secrets.toml into the environment if present (keys may already be set).
    if args.secrets and os.path.exists(args.secrets):
        from knowledge_storm.utils import load_api_key

        load_api_key(toml_file_path=args.secrets)

    if not os.getenv("ANTHROPIC_API_KEY"):
        return _fail(
            {
                "ok": False,
                "error": "ANTHROPIC_API_KEY is not set.",
                "hint": "Export ANTHROPIC_API_KEY or put it in secrets.toml. "
                "Note: this is an Anthropic API key, not the Claude Code subscription.",
            },
            2,
        )

    missing = missing_retriever_key(args.retriever)
    if missing:
        return _fail(
            {
                "ok": False,
                "error": f"Retriever {args.retriever!r} requires {missing}, which is not set.",
                "hint": "Set the key, or use '--retriever duckduckgo' (no key required).",
            },
            3,
        )

    try:
        summary = run_pipeline(args)
    except Exception as exc:  # noqa: BLE001 - surface any failure as JSON for the agent.
        return _fail(
            {"ok": False, "error": str(exc), "type": type(exc).__name__, "topic": args.topic},
            1,
        )

    # Persist the summary next to the article for the skill to poll.
    try:
        summary_path = os.path.join(summary["output_dir"], "claude_code_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        summary["summary_path"] = summary_path
    except OSError:
        pass

    if args.print_summary:
        print(json.dumps(summary, ensure_ascii=False))
    else:
        print(f"[storm-claude] done -> {summary.get('article_path')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
