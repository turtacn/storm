# Vendored third-party skills

The following skill directories under `.claude/skills/` are **vendored verbatim**
from a third-party project so this repository is self-contained (no external
install script, archive, or globally-installed skill is required):

| Vendored skill | Purpose |
|---|---|
| `grill-with-docs/` | One-line entry skill; delegates to the two below |
| `grilling/` | The relentless interview primitive |
| `domain-modeling/` | Writes the glossary (`CONTEXT.md`) and ADRs (`docs/adr/`) as terms/decisions resolve; includes `ADR-FORMAT.md` + `CONTEXT-FORMAT.md` |

(`storm-research/` in this same directory is **first-party** to this repo and is
NOT covered by this notice.)

## Source & provenance

- Upstream: https://github.com/mattpocock/skills
- Commit pinned: `c55ee46073ed923f86ce59a5eb3b6d895095d1b7`
- Upstream paths:
  - `skills/engineering/grill-with-docs/SKILL.md`
  - `skills/engineering/domain-modeling/{SKILL.md,ADR-FORMAT.md,CONTEXT-FORMAT.md}`
  - `skills/productivity/grilling/SKILL.md`
- License: MIT (see full text below).

### What was intentionally omitted

- `agents/openai.yaml` from each upstream skill — those configure the skills for
  the OpenAI/Codex harness and are irrelevant to Claude Code self-containment.
- The downstream build chain (`to-spec` → `to-tickets` → `implement` →
  `code-review`) — not vendored. `grill-with-docs` runs without them; it produces
  `CONTEXT.md` + ADRs and suggests next steps.

### Note on a global copy

Some environments already have Matt Pocock's pack installed globally (the session's
`grilling` skill is the same one). The vendored copies here are identical in
behaviour; keeping a project copy is deliberate so a fresh clone of this fork works
without any global install. If a name collision ever matters, the project-scoped
copy is the self-contained source of truth for this repo.

### How to refresh

```bash
SHA=<upstream-commit>
BASE="https://raw.githubusercontent.com/mattpocock/skills/$SHA/skills"
curl -sSfL "$BASE/engineering/grill-with-docs/SKILL.md"          -o .claude/skills/grill-with-docs/SKILL.md
curl -sSfL "$BASE/engineering/domain-modeling/SKILL.md"          -o .claude/skills/domain-modeling/SKILL.md
curl -sSfL "$BASE/engineering/domain-modeling/ADR-FORMAT.md"     -o .claude/skills/domain-modeling/ADR-FORMAT.md
curl -sSfL "$BASE/engineering/domain-modeling/CONTEXT-FORMAT.md" -o .claude/skills/domain-modeling/CONTEXT-FORMAT.md
curl -sSfL "$BASE/productivity/grilling/SKILL.md"                -o .claude/skills/grilling/SKILL.md
```

---

## MIT License (upstream)

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
