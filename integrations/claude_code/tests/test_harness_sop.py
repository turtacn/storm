"""Self-containment checks for the competitive-analysis harness SOP.

Guards that the SOP skill, its documentation home under docs/harness-sop/, the report
outline, the examples directory and the slash command are all present and wired to the
skills the SOP orchestrates. Stdlib-only.
"""

import os
import re
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TESTS_DIR)))

SKILL = os.path.join(REPO_ROOT, ".claude", "skills", "competitive-analysis", "SKILL.md")
COMMAND = os.path.join(REPO_ROOT, ".claude", "commands", "compare.md")
SOP_DIR = os.path.join(REPO_ROOT, "docs", "harness-sop")


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def frontmatter_name(path):
    m = re.match(r"^---\n(.*?)\n---\n", read(path), re.DOTALL)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


class HarnessSopTests(unittest.TestCase):
    def test_skill_present_and_named(self):
        self.assertTrue(os.path.exists(SKILL), "competitive-analysis SKILL.md missing")
        self.assertEqual(frontmatter_name(SKILL), "competitive-analysis")

    def test_docs_home_present(self):
        for rel in (
            "README.md",
            "report-outline.md",
            "value-realization-model.md",
            os.path.join("examples", "README.md"),
        ):
            self.assertTrue(
                os.path.exists(os.path.join(SOP_DIR, rel)),
                f"docs/harness-sop/{rel} missing",
            )

    def test_value_spine_present(self):
        # The SOP is organized around value realization: phase 0 + traceability.
        body = read(SKILL)
        self.assertIn("阶段零", body)
        self.assertIn("value-realization-model.md", body)

    def test_command_present(self):
        self.assertTrue(os.path.exists(COMMAND), "/compare command missing")

    def test_skill_orchestrates_expected_skills(self):
        body = read(SKILL)
        for dep in ("grilling", "storm-research", "report-authoring"):
            self.assertIn(dep, body, f"SOP should orchestrate '{dep}'")

    def test_skill_points_to_docs_home(self):
        body = read(SKILL)
        self.assertIn("docs/harness-sop/report-outline.md", body)
        self.assertIn("docs/harness-sop/examples/", body)


if __name__ == "__main__":
    unittest.main()
