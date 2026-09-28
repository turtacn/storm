"""Tests for the integration preflight checker. Stdlib-only; no STORM deps."""

import io
import contextlib
import json
import os
import sys
import unittest

PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PKG_DIR not in sys.path:
    sys.path.insert(0, PKG_DIR)

import preflight  # noqa: E402


class _env:
    def __init__(self, **kwargs):
        self._new = kwargs
        self._old = {}

    def __enter__(self):
        for key, val in self._new.items():
            self._old[key] = os.environ.get(key)
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val
        return self

    def __exit__(self, *exc):
        for key, val in self._old.items():
            if val is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = val
        return False


class PreflightTests(unittest.TestCase):
    def test_python_check_passes(self):
        # The interpreter running the tests is >= 3.10 (STORM's floor).
        self.assertTrue(preflight.check_python()["ok"])

    def test_anthropic_key_check(self):
        with _env(ANTHROPIC_API_KEY=None):
            self.assertFalse(preflight.check_anthropic_key()["ok"])
        with _env(ANTHROPIC_API_KEY="sk-x"):
            self.assertTrue(preflight.check_anthropic_key()["ok"])

    def test_retriever_key_check(self):
        self.assertTrue(preflight.check_retriever_key("duckduckgo")["ok"])
        with _env(BING_SEARCH_API_KEY=None):
            self.assertFalse(preflight.check_retriever_key("bing")["ok"])
        with _env(TAVILY_API_KEY="x"):
            self.assertTrue(preflight.check_retriever_key("tavily")["ok"])

    def test_retriever_dep_check(self):
        # DuckDuckGo (keyless default) needs the duckduckgo_search package.
        r = preflight.check_retriever_dep("duckduckgo")
        self.assertIn("ok", r)
        self.assertIn("hint", r)
        if not r["ok"]:
            self.assertIn("requirements-extra", r["hint"])
        # retrievers without an extra dep report n/a-ok
        self.assertTrue(preflight.check_retriever_dep("bing")["ok"])

    def test_import_check_reports_status(self):
        # In this environment the STORM stack isn't installed, so this reports
        # not-ok with an actionable hint. The shape must always be well-formed.
        result = preflight.check_import("knowledge_storm")
        self.assertIn("ok", result)
        self.assertIn("hint", result)
        if not result["ok"]:
            self.assertIn("pip install", result["hint"])

    def test_build_report_ok_depends_on_all_checks(self):
        report = preflight.build_report("duckduckgo")
        self.assertEqual(report["ok"], all(c["ok"] for c in report["checks"]))
        self.assertEqual(report["retriever"], "duckduckgo")

    def test_main_exit_code_matches_ok(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), _env(
            ANTHROPIC_API_KEY="sk-x"
        ):
            rc = preflight.main(["--retriever", "duckduckgo", "--secrets", "___nope___.toml"])
        report = json.loads(out.getvalue())
        self.assertEqual(rc, 0 if report["ok"] else 1)


if __name__ == "__main__":
    unittest.main()
