"""Enforce the repo Mermaid style on authored docs under docs/.

Rule (see docs/authoring/mermaid-style-guide.md): inside ```mermaid fences, text must
use full-width parentheses （） not ASCII ( ), and line breaks must be <br> not a
literal \\n. This scans only the repo's own docs/ tree (not vendor/, which is verbatim
third-party source). Stdlib-only; runs under pytest or `python3 -m unittest`.
"""

import os
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TESTS_DIR)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")


def iter_mermaid_blocks(md_text):
    """Yield (start_lineno, [(lineno, line), ...]) for each ```mermaid fence."""
    lines = md_text.splitlines()
    inside = False
    block = []
    start = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not inside and stripped.startswith("```mermaid"):
            inside, block, start = True, [], i
            continue
        if inside and stripped == "```":
            yield start, block
            inside = False
            continue
        if inside:
            block.append((i, line))


def md_files(root):
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)


class MermaidStyleTests(unittest.TestCase):
    def test_no_ascii_parens_or_backslash_n_in_mermaid(self):
        violations = []
        for md in md_files(DOCS_DIR):
            with open(md, "r", encoding="utf-8") as fh:
                text = fh.read()
            rel = os.path.relpath(md, REPO_ROOT)
            for _start, block in iter_mermaid_blocks(text):
                for lineno, line in block:
                    if "(" in line or ")" in line:
                        violations.append(f"{rel}:{lineno} ASCII paren -> {line.strip()}")
                    if "\\n" in line:
                        violations.append(f"{rel}:{lineno} literal backslash-n -> {line.strip()}")
        self.assertEqual(
            violations, [], "Mermaid style violations:\n" + "\n".join(violations)
        )

    def test_docs_carry_mermaid_diagrams(self):
        count = 0
        for md in md_files(DOCS_DIR):
            with open(md, "r", encoding="utf-8") as fh:
                count += sum(1 for _ in iter_mermaid_blocks(fh.read()))
        self.assertGreater(count, 0, "expected at least one mermaid diagram under docs/")


if __name__ == "__main__":
    unittest.main()
