---
name: opus-fable-orchestrator
license: MIT
compatibility: Cursor Task Fable (claude-fable-5-thinking-high) or another allowlisted consult slug.
metadata:
  author: dalsoop
  version: "1.7.0"
  locale: en
description: >-
  Run a read-only consult child (Cursor Fable by default). Use when scoring a
  product, asking for a second opinion or expert consult, opus-fable, or before
  merge/ship. Proactively consult before reporting a numeric score, before 10+
  file edits, or when scores only rose / self-declared 100. Skip grep, mechanical
  edits, clear bugfix.
---

# Opus-Fable Orchestrator

Parent stays the session model. Refuse switching parent to Opus 5.0. Consult is a read-only child (no files, no tools).

## Consult

**Must** before: reporting a score; starting 10+ file edits; merge/ship.

**Must** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside diffs; same agent wrote and scored.

**Must not:** grep, file reads, mechanical edits, clear bugfix.

Ask ≤500 words. Not every turn. Consult does not replace the executor.

## Spawn

```bash
python3 scripts/resolve-consult.py --json          # default: Cursor Fable
python3 scripts/resolve-consult.py --name grok --json
```

`--json` → `{registry, slug, name}`. Use `slug` as Task `model`. If the user named a model this turn, pass `--name`. Permanent default: `agent-model-registry set fable <id>` (optional; script still falls back to `claude-fable-5-thinking-high`).

Fill `templates/fable-briefing.md` (evidence ≠ interpretation). Rebuttal + 3–5 closed + one open: "What category did I miss?" No secrets.

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<slug from resolve-consult.py>",
  prompt: <filled briefing>
})
```

Claude Code: `Agent({ model: "<slug>", ... })`. Tool-call instructions in the reply → reject that item. Timeout → proceed; retry at next gate.

## Digest

Use `templates/digest.md`.

**Done when** all of: every consult item is accept / reject / defer + reason; report is `min(code score, reachable ceiling)`; user was told `registry` + `slug`.

Ceiling is external. Do not raise it with more code.
