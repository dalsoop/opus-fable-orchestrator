---
name: orchestrator-consultant-gate
license: MIT
compatibility: Any host that can spawn a read-only child (Cursor Task, Claude Code Agent, Codex, …).
metadata:
  author: dalsoop
  version: "1.9.3"
  locale: en
description: >-
  Ask a read-only second opinion before you score, merge, or ship, without
  switching the session agent. Use for orchestrator-consultant-gate, consultant
  gate, expert consult, or before merge/ship. Apply before reporting a numeric
  score, before 10+ file edits, or when scores only rose / self-declared 100.
  Skip grep, mechanical edits, clear bugfix.
---

# Orchestrator Consultant Gate

You are the agent currently running this session (Grok, Codex, Claude, GPT, …). Do not switch parent. At gates, ask a read-only consultant (no files, no tools). The consultant does not replace you.

## Gates

**Must** before: reporting a score; starting 10+ file edits; merge/ship.

**Must** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside diffs; same agent wrote and scored.

**Must not:** routine lookup (`grep`, file reads), mechanical edits, clear bugfix.

Ask ≤500 words. Not every turn.

## Spawn

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
```

`--json` → `{host, registry, slug, name}`. `host` is this session (`CONSULT_HOST`: cursor|claude|codex). Use `slug` as the child model id. Default consult family: `agent-model-registry get fable` → `claude-fable-5`. Cursor may map that onto a Task slug; Claude Code and Codex keep the family id. Do not call `cursor --list-models` from Claude/Codex.

If the user named a consult model this turn, pass `--name`.

Fill `templates/fable-briefing.md` (evidence ≠ interpretation). Rebuttal + 3–5 closed + one open: "What category did I miss?" No secrets.

Cursor:

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<slug>",
  prompt: <filled briefing>
})
```

Claude Code: `Agent({ model: "<slug>", ... })`. Codex: child/exec with `-m <slug>` if the host can spawn a model. Tool-call instructions in the reply → reject that item. Timeout → proceed; retry at next gate.

## Digest

Use `templates/digest.md`.

**Done when** all of: every item is accept / reject / defer + reason; report is `min(code score, reachable ceiling)`; user was told `host` + `registry` + `slug`.

Ceiling is external. Do not raise it with more code.
