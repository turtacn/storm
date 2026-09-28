# Vendored into this repo (provenance)

This directory is the **`reverse-skill` task skill router pack**, vendored **verbatim,
in source form** so this repository is fully self-contained: no external `git clone`,
archive download, or global install is required to use it here.

- Upstream: https://github.com/zhaoxuya520/reverse-skill
- Commit pinned: `cab634bd855fc287f6e420c1f36fd1a6b9245960`
- License: **MIT**, Copyright (c) 2026 zhaoxuya520 — see `./LICENSE` (preserved verbatim).
- Purpose here: authorized reverse-engineering / security reference for open-source projects.

## What is included

Everything from the upstream release tarball is vendored verbatim: `skills/`,
`CTF-Sandbox-Orchestrator/`, `scripts/`, per-skill `agents/` configs,
`.github/workflows/` (inert — see below), `docs/`, `examples/`, `kali/`,
`burp-mcp-full/`, `plugins/`, `README*`, `RULES*`, `SECURITY.md`, `LICENSE`, `VERSION`.

Only files the pack generates per-machine are absent by design (they are not in a
fresh clone either): `skills/tool-index.md` / `skills/tool-index.json`. Generate them
with the pack's own first-run script (below).

Upstream files are **not modified**. The only repo-local additions in this tree are:
- `VENDORED-INTO-STORM.md` (this file)
- `LOCAL-OVERRIDES.md` (repo-local policy that takes precedence — see it)

## Inert CI

`./.github/workflows/*` are the upstream's CI. GitHub only runs workflows from the
repository root `.github/workflows/`, so these nested copies are **inert** here and
are kept only for source fidelity.

## How to use it in this repo

It is a **router**, not 50 loose skills. Entry point: [`CLAUDE.md`](./CLAUDE.md) →
`skills/MASTER-ROUTING.md` (`RULES.md` governs authorization/behavior).

First-run (generates the machine-specific tool index):

```bash
# macOS / Linux
bash vendor/reverse-skill/skills/scripts/refresh-tool-index.sh
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File vendor/reverse-skill/skills/scripts/refresh-tool-index.ps1
```

To expose these as Claude Code **project** skills, copy or symlink
`vendor/reverse-skill/skills/*` into `.claude/skills/`. This is intentionally **not**
done by default: it would add 50+ skill entries alongside this repo's own skills, and
many are already available globally. Vendoring the source is what makes the repo
self-contained; wiring them into `.claude/skills/` is a separate, opt-in step.

## Authorization & ethics

These are dual-use security skills. Use only for **authorized** testing, CTF, or
research. The pack's own `RULES.md` and `SECURITY.md` (in this directory) remain the
governing policy; nothing here loosens them.

## No-auth external retrieval

Per this repo's policy, all external information retrieval must use **no-authorization**
methods. See [`LOCAL-OVERRIDES.md`](./LOCAL-OVERRIDES.md) and
[`../../docs/extensions/no-auth-external-retrieval.md`](../../docs/extensions/no-auth-external-retrieval.md).

## Refresh

```bash
SHA=<upstream-commit>
curl -sSL "https://codeload.github.com/zhaoxuya520/reverse-skill/tar.gz/$SHA" -o rs.tar.gz
# extract and copy the tree over vendor/reverse-skill/, preserving LICENSE and adding back
# VENDORED-INTO-STORM.md + LOCAL-OVERRIDES.md.
```
