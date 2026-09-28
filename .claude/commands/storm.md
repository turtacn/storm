---
description: Research a topic with STORM (Claude-backed) and produce a cited, Wikipedia-style article
argument-hint: <topic>
---

Use the `storm-research` skill to research and write a cited, Wikipedia-style
article about the following topic:

$ARGUMENTS

Follow the skill exactly: run preflight first, launch the STORM run in the
background (it takes minutes), poll for `claude_code_summary.json`, then present a
short digest with the article path and offer to publish it as an Artifact. If no
topic was provided above, ask the user for one before doing anything else.
