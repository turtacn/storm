"""Tests for the Claude-backed STORM runner.

These run without the STORM dependency stack: a fake ``knowledge_storm`` package
is injected into ``sys.modules`` so the wrapper's real plumbing (argument parsing,
model/slot assignment, stage resolution, summary building, file output) is
exercised end-to-end. Runnable with either ``pytest`` or ``python3 -m unittest``.
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import types
import unittest

# Make the wrapper importable (it lives one directory up from tests/).
PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PKG_DIR not in sys.path:
    sys.path.insert(0, PKG_DIR)

import run_storm_claude as rsc  # noqa: E402


# --------------------------------------------------------------------------- #
# Fakes                                                                        #
# --------------------------------------------------------------------------- #
class FakeLitellmModel:
    instances = []

    def __init__(self, model, max_tokens, **kwargs):
        self.model = model
        self.max_tokens = max_tokens
        self.kwargs = kwargs
        self.history = []
        FakeLitellmModel.instances.append(self)

    def get_usage_and_reset(self):
        return {self.model: {"prompt_tokens": 0, "completion_tokens": 0}}


class FakeLMConfigs:
    def __init__(self):
        self.slots = {}

    def set_conv_simulator_lm(self, m):
        self.slots["conv_simulator_lm"] = m

    def set_question_asker_lm(self, m):
        self.slots["question_asker_lm"] = m

    def set_outline_gen_lm(self, m):
        self.slots["outline_gen_lm"] = m

    def set_article_gen_lm(self, m):
        self.slots["article_gen_lm"] = m

    def set_article_polish_lm(self, m):
        self.slots["article_polish_lm"] = m


class FakeRunnerArguments:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeDuckDuckGoSearchRM:
    def __init__(self, k=3, safe_search="On", region="us-en"):
        self.k = k


class FakeRunner:
    last = None

    def __init__(self, args, lm_configs, rm):
        self.args = args
        self.lm_configs = lm_configs
        self.rm = rm
        self.time = {}
        self.lm_cost = {}
        self.rm_cost = {}
        self.run_kwargs = None
        self.article_output_dir = None
        FakeRunner.last = self

    def _w(self, name, content):
        with open(os.path.join(self.article_output_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    def run(self, topic, remove_duplicate=False, **stages):
        self.run_kwargs = dict(stages)
        self.remove_duplicate = remove_duplicate
        slug = topic.replace(" ", "_").replace("/", "_")
        self.article_output_dir = os.path.join(self.args.output_dir, slug)
        os.makedirs(self.article_output_dir, exist_ok=True)
        if stages.get("do_research"):
            self._w("conversation_log.json", "[]")
            self._w("raw_search_results.json", "{}")
        if stages.get("do_generate_outline"):
            self._w("storm_gen_outline.txt", "# Outline")
            self._w("direct_gen_outline.txt", "# Draft outline")
        if stages.get("do_generate_article"):
            self._w("storm_gen_article.txt", "draft body")
            self._w(
                "url_to_info.json",
                json.dumps({"url_to_unified_index": {"http://a": 1, "http://b": 2}}),
            )
        if stages.get("do_polish_article"):
            self._w("storm_gen_article_polished.txt", "# Title\n\npolished body")
        self.lm_cost = {"run_article_generation_module": {"strong": {"prompt_tokens": 10}}}
        self.time = {"run_article_generation_module": 1.0}
        self.rm_cost = {"run_knowledge_curation_module": {"DuckDuckGoSearchRM": 3}}

    def post_run(self):
        self._w("run_config.json", "{}")
        self._w("llm_call_history.jsonl", "")


def install_fake_storm():
    """Inject a fake knowledge_storm package tree into sys.modules."""
    ks = types.ModuleType("knowledge_storm")
    ks.STORMWikiRunner = FakeRunner
    ks.STORMWikiRunnerArguments = FakeRunnerArguments
    ks.STORMWikiLMConfigs = FakeLMConfigs

    lm = types.ModuleType("knowledge_storm.lm")
    lm.LitellmModel = FakeLitellmModel

    rm = types.ModuleType("knowledge_storm.rm")
    rm.DuckDuckGoSearchRM = FakeDuckDuckGoSearchRM

    utils = types.ModuleType("knowledge_storm.utils")
    utils.load_api_key = lambda toml_file_path=None: None

    ks.lm = lm
    ks.rm = rm
    ks.utils = utils
    modules = {
        "knowledge_storm": ks,
        "knowledge_storm.lm": lm,
        "knowledge_storm.rm": rm,
        "knowledge_storm.utils": utils,
    }
    sys.modules.update(modules)
    return modules


# --------------------------------------------------------------------------- #
# Pure-function tests (no fakes needed)                                        #
# --------------------------------------------------------------------------- #
class PureLogicTests(unittest.TestCase):
    def test_parser_defaults(self):
        args = rsc.build_parser().parse_args(["--topic", "Quantum error correction"])
        self.assertEqual(args.topic, "Quantum error correction")
        self.assertEqual(args.retriever, "duckduckgo")
        self.assertEqual(args.output_dir, "./results/claude_code")
        self.assertFalse(args.print_summary)

    def test_stages_default_all_on(self):
        args = rsc.build_parser().parse_args(["--topic", "X"])
        stages = rsc.resolve_stages(args)
        self.assertTrue(all(stages.values()))
        self.assertEqual(set(stages), {
            "do_research",
            "do_generate_outline",
            "do_generate_article",
            "do_polish_article",
        })

    def test_stages_subset(self):
        args = rsc.build_parser().parse_args(
            ["--topic", "X", "--do-research", "--do-generate-outline"]
        )
        stages = rsc.resolve_stages(args)
        self.assertTrue(stages["do_research"])
        self.assertTrue(stages["do_generate_outline"])
        self.assertFalse(stages["do_generate_article"])
        self.assertFalse(stages["do_polish_article"])

    def test_model_plan_tiers(self):
        args = rsc.build_parser().parse_args(
            ["--topic", "X", "--strong-model", "S", "--fast-model", "F"]
        )
        plan = rsc.resolve_model_plan(args)
        self.assertEqual(plan["article_gen_lm"]["model"], "S")
        self.assertEqual(plan["outline_gen_lm"]["model"], "S")
        self.assertEqual(plan["article_polish_lm"]["model"], "S")
        self.assertEqual(plan["conv_simulator_lm"]["model"], "F")
        self.assertEqual(plan["question_asker_lm"]["model"], "F")
        self.assertEqual(plan["article_polish_lm"]["max_tokens"], 4000)

    def test_missing_retriever_key(self):
        self.assertIsNone(rsc.missing_retriever_key("duckduckgo"))
        with _env(BING_SEARCH_API_KEY=None):
            self.assertEqual(rsc.missing_retriever_key("bing"), "BING_SEARCH_API_KEY")
        with _env(BING_SEARCH_API_KEY="x"):
            self.assertIsNone(rsc.missing_retriever_key("bing"))


# --------------------------------------------------------------------------- #
# End-to-end tests (with fakes)                                                #
# --------------------------------------------------------------------------- #
class MainWithFakesTests(unittest.TestCase):
    def setUp(self):
        FakeLitellmModel.instances = []
        FakeRunner.last = None
        self._saved = {k: sys.modules.get(k) for k in (
            "knowledge_storm",
            "knowledge_storm.lm",
            "knowledge_storm.rm",
            "knowledge_storm.utils",
        )}
        install_fake_storm()

    def tearDown(self):
        for key, val in self._saved.items():
            if val is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = val

    def test_full_run_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmp, _env(ANTHROPIC_API_KEY="sk-test"):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = rsc.main([
                    "--topic", "Large Language Models",
                    "--output-dir", tmp,
                    "--strong-model", "anthropic/claude-strong",
                    "--fast-model", "anthropic/claude-fast",
                    "--secrets", os.path.join(tmp, "nope.toml"),
                    "--print-summary",
                ])
            self.assertEqual(rc, 0)
            summary = json.loads(out.getvalue().strip().splitlines()[-1])

            # Summary shape and content.
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["topic"], "Large Language Models")
            self.assertTrue(summary["article_path"].endswith("storm_gen_article_polished.txt"))
            self.assertEqual(summary["num_references"], 2)
            self.assertEqual(len(summary["stages_run"]), 4)
            self.assertEqual(summary["models"]["article_gen_lm"], "anthropic/claude-strong")
            self.assertEqual(summary["models"]["conv_simulator_lm"], "anthropic/claude-fast")

            # Summary persisted next to the article.
            summary_file = os.path.join(summary["output_dir"], "claude_code_summary.json")
            self.assertTrue(os.path.exists(summary_file))

            # Five LM slots instantiated; strong model wired to article generation.
            self.assertEqual(len(FakeLitellmModel.instances), 5)
            self.assertEqual(
                FakeRunner.last.lm_configs.slots["article_gen_lm"].model,
                "anthropic/claude-strong",
            )
            # Runner received all four stage flags as True.
            self.assertTrue(all(FakeRunner.last.run_kwargs.values()))

    def test_missing_anthropic_key_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp, _env(ANTHROPIC_API_KEY=None):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = rsc.main([
                    "--topic", "X",
                    "--output-dir", tmp,
                    "--secrets", os.path.join(tmp, "nope.toml"),
                ])
            self.assertEqual(rc, 2)
            payload = json.loads(out.getvalue().strip())
            self.assertFalse(payload["ok"])
            self.assertIn("ANTHROPIC_API_KEY", payload["error"])

    def test_missing_retriever_key_exits_3(self):
        with tempfile.TemporaryDirectory() as tmp, _env(
            ANTHROPIC_API_KEY="sk-test", BING_SEARCH_API_KEY=None
        ):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = rsc.main([
                    "--topic", "X",
                    "--output-dir", tmp,
                    "--retriever", "bing",
                    "--secrets", os.path.join(tmp, "nope.toml"),
                ])
            self.assertEqual(rc, 3)
            payload = json.loads(out.getvalue().strip())
            self.assertFalse(payload["ok"])
            self.assertIn("BING_SEARCH_API_KEY", payload["error"])


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
class _env:
    """Context manager to set/unset env vars (value None removes the var)."""

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


if __name__ == "__main__":
    unittest.main()
