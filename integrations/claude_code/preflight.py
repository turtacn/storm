#!/usr/bin/env python3
"""Preflight checks for the STORM <-> Claude Code integration.

The ``storm-research`` skill runs this first so it can give the user a precise,
actionable status instead of a mid-run stack trace. It verifies:

* Python version (STORM needs >= 3.10).
* That ``knowledge_storm`` and its heavy deps import.
* That ``ANTHROPIC_API_KEY`` is available (optionally after loading secrets.toml).
* That the selected retriever's API key is present (DuckDuckGo needs none).

It prints a JSON report to stdout and exits 0 when ready, 1 otherwise. Every
check is best-effort and never raises; the report always lists what to fix.
"""

import argparse
import importlib
import json
import os
import sys

# Retriever -> required key env var (None = keyless). Kept in sync with
# run_storm_claude.RETRIEVER_ENV; duplicated here so preflight has no import-time
# dependency on the STORM stack.
RETRIEVER_ENV = {
    "duckduckgo": None,
    "searxng": None,
    "bing": "BING_SEARCH_API_KEY",
    "you": "YDC_API_KEY",
    "serper": "SERPER_API_KEY",
    "brave": "BRAVE_API_KEY",
    "tavily": "TAVILY_API_KEY",
}

MIN_PYTHON = (3, 10)


def check_python() -> dict:
    ok = sys.version_info[:2] >= MIN_PYTHON
    return {
        "name": "python_version",
        "ok": ok,
        "detail": ".".join(map(str, sys.version_info[:3])),
        "hint": None if ok else "STORM requires Python >= 3.10 (3.11 recommended).",
    }


def check_import(module: str = "knowledge_storm") -> dict:
    try:
        importlib.import_module(module)
        return {"name": f"import:{module}", "ok": True, "detail": "importable", "hint": None}
    except Exception as exc:  # noqa: BLE001 - import may fail many ways.
        return {
            "name": f"import:{module}",
            "ok": False,
            "detail": f"{type(exc).__name__}: {exc}",
            "hint": "Install deps: python3 -m venv .venv && . .venv/bin/activate "
            "&& pip install -r requirements.txt",
        }


def check_anthropic_key() -> dict:
    ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "name": "ANTHROPIC_API_KEY",
        "ok": ok,
        "detail": "set" if ok else "missing",
        "hint": None
        if ok
        else "Export ANTHROPIC_API_KEY or add it to secrets.toml (Anthropic API key, "
        "not the Claude Code subscription).",
    }


def check_retriever_key(retriever: str) -> dict:
    env_var = RETRIEVER_ENV.get(retriever)
    if env_var is None:
        return {
            "name": f"retriever:{retriever}",
            "ok": True,
            "detail": "no key required",
            "hint": None,
        }
    ok = bool(os.getenv(env_var))
    return {
        "name": f"retriever:{retriever}",
        "ok": ok,
        "detail": f"{env_var} {'set' if ok else 'missing'}",
        "hint": None if ok else f"Set {env_var}, or use --retriever duckduckgo (keyless).",
    }


def build_report(retriever: str = "duckduckgo") -> dict:
    checks = [
        check_python(),
        check_import(),
        check_anthropic_key(),
        check_retriever_key(retriever),
    ]
    return {"ok": all(c["ok"] for c in checks), "retriever": retriever, "checks": checks}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="preflight", description=__doc__)
    parser.add_argument("--retriever", default="duckduckgo", choices=sorted(RETRIEVER_ENV))
    parser.add_argument(
        "--secrets",
        default="secrets.toml",
        help="Optional TOML file of API keys to load before checking.",
    )
    args = parser.parse_args(argv)

    # Load secrets first so key checks reflect what a real run would see.
    if args.secrets and os.path.exists(args.secrets):
        try:
            import toml

            for key, value in toml.load(args.secrets).items():
                os.environ.setdefault(key, str(value))
        except Exception:  # noqa: BLE001 - missing toml lib or bad file is non-fatal.
            pass

    report = build_report(args.retriever)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
