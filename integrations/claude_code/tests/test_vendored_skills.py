"""Self-containment checks for the vendored grilling suite under .claude/skills/.

These guard the invariant that `grill-with-docs` and its dependency chain are
fully present in this repo, so a fresh clone works without any global install.
Stdlib-only; no STORM deps. Runs under pytest or `python3 -m unittest`.
"""

import os
import re
import unittest

# repo root = three levels up from this tests/ directory.
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TESTS_DIR)))
SKILLS_DIR = os.path.join(REPO_ROOT, ".claude", "skills")

VENDORED = ("grill-with-docs", "grilling", "domain-modeling")


def frontmatter_name(skill_md_path):
    """Return the `name:` value from a SKILL.md YAML frontmatter block."""
    with open(skill_md_path, "r", encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    for line in m.group(1).splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class VendoredSkillsTests(unittest.TestCase):
    def test_each_vendored_skill_present_with_matching_name(self):
        for skill in VENDORED:
            skill_md = os.path.join(SKILLS_DIR, skill, "SKILL.md")
            self.assertTrue(os.path.exists(skill_md), f"missing {skill}/SKILL.md")
            self.assertEqual(
                frontmatter_name(skill_md),
                skill,
                f"{skill}/SKILL.md frontmatter name must equal '{skill}'",
            )

    def test_grill_with_docs_delegations_are_all_vendored(self):
        # Every skill grill-with-docs delegates to (quoted names in its body)
        # must exist as a vendored skill -> the delegation is self-contained.
        body = read(os.path.join(SKILLS_DIR, "grill-with-docs", "SKILL.md"))
        body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.DOTALL)  # drop frontmatter
        delegated = set(re.findall(r'"([a-z0-9-]+)"', body))
        self.assertIn("grilling", delegated)
        self.assertIn("domain-modeling", delegated)
        present = {
            d for d in os.listdir(SKILLS_DIR)
            if os.path.exists(os.path.join(SKILLS_DIR, d, "SKILL.md"))
        }
        missing = delegated - present
        self.assertEqual(missing, set(), f"grill-with-docs delegates to un-vendored skills: {missing}")

    def test_domain_modeling_support_files_present(self):
        dm = os.path.join(SKILLS_DIR, "domain-modeling")
        body = read(os.path.join(dm, "SKILL.md"))
        for ref in ("ADR-FORMAT.md", "CONTEXT-FORMAT.md"):
            self.assertIn(ref, body, f"domain-modeling should reference {ref}")
            self.assertTrue(
                os.path.exists(os.path.join(dm, ref)),
                f"domain-modeling/{ref} must be vendored",
            )

    def test_vendor_notice_carries_mit_attribution(self):
        notice = os.path.join(SKILLS_DIR, "VENDOR-NOTICE.md")
        self.assertTrue(os.path.exists(notice), "VENDOR-NOTICE.md missing")
        text = read(notice)
        self.assertIn("MIT", text)
        self.assertIn("Copyright (c) 2026 Matt Pocock", text)

    def test_no_codex_agent_configs_vendored(self):
        # We intentionally omit the upstream agents/openai.yaml (Codex-specific).
        for skill in VENDORED:
            agents = os.path.join(SKILLS_DIR, skill, "agents")
            self.assertFalse(
                os.path.exists(agents),
                f"unexpected Codex agents/ dir vendored under {skill}/",
            )


if __name__ == "__main__":
    unittest.main()
