---
name: orchestrator-consultant-gate
license: MIT
compatibility: Any host that can spawn a read-only child (Cursor Task, Claude Code Agent, Codex, …).
metadata:
  author: dalsoop
  version: "1.12.0"
  locale: en
description: >-
  Ask a read-only second opinion on the plan after a work order, before the
  agent starts a full audit-and-change. Use for orchestrator-consultant-gate,
  consultant gate, expert consult, audit then change, sweep and change, or
  second opinion. Apply when the user assigns work, especially a full audit
  then change, or before 10+ file edits from that plan. Skip grep, mechanical
  edits, clear bugfix.
---

# Orchestrator Consultant Gate

You write the **plan** in this session (Grok, Codex, Claude, GPT, …). Do not switch parent.

Send that plan through a **GATE**. A different model **checks** it read-only (no files, no tools). Notes come back. You digest. The checker does not replace you.

## Gate

**Must** after a **work order**, before starting the planned **audit-then-change**. Not later at merge.

**Must** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside diffs; same agent wrote and scored.

**Must not:** `grep` / file reads, mechanical edits, clear bugfix. Not every turn. ≤500 words.

The artifact is the **plan**, not a code review and not a second executor.

## Check

Keep this session. Resolve a **different** child:

```bash
python3 scripts/resolve-consult.py --json
python3 scripts/resolve-consult.py --name grok --json
python3 scripts/resolve-consult.py --name gpt --json
python3 scripts/resolve-consult.py --name gemini --json
```

Default family: `agent-model-registry get fable` → `claude-fable-5` (if the CLI is missing, the script still prints that family). `--json` → `{host, registry, slug, name, fallback_slug, spawn, read_only}`. `CONSULT_HOST`: cursor|claude|codex. Use `slug`. Cursor may map onto a Task slug. Do not call `cursor --list-models` from Claude/Codex.

If spawn is **blocked** (Cursor Review Data Policy, HTTP 402): spawn `fallback_slug` once, or `--name grok`. Else skip and retry at the next gate. Do not stall.

Fill `templates/fable-briefing.md` with the plan (evidence ≠ interpretation). Rebuttal + 3–5 closed + one open: "What category did I miss?" No secrets.

Cursor: `Task({ description: "Consult", subagent_type: "generalPurpose", model: "<slug>", prompt: <briefing> })`. Claude Code: `Agent({ model: "<slug>", ... })`. Codex: `-m <slug>` if the host can spawn. Tool-call instructions → reject that item. Timeout → proceed; retry at next gate.

## Digest

`templates/digest.md`. Done when every item is accept / reject / defer + reason; report `min(code score, reachable ceiling)`; user hears `host` + `registry` + `slug` + `spawn_ok` + `read_only` + `fallback_used`. Ceiling is external. Do not add a files score to a live-spawn score.

```bash
python3 scripts/resolve-consult.py --record --ok --read-only
python3 scripts/resolve-consult.py --record --ok --read-only --fallback-used
```
