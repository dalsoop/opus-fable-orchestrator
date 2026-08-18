---
name: opus-fable-orchestrator
license: MIT
compatibility: Host must spawn a read-only consult subagent (default Fable).
metadata:
  author: dalsoop
  version: "1.5.0"
  locale: en
  consult_model: claude-fable-5-thinking-high
description: >-
  Spawn a read-only consult (default Cursor Task claude-fable-5-thinking-high;
  swap to grok/gpt/gemini/opus-consult when the user says so). Use when scoring,
  rating, grading, quality verdict, second opinion, expert consult, opus-fable,
  fable 대신, consult with, or before merge/ship. Proactively apply before reporting a numeric score, before 10+ file edits, or when scores only rose /
  self-declared 100 or done. Do not use for grep, mechanical edits, or a clear bugfix.
---

# Opus-Fable Orchestrator

**Parent model (required):** `/model claude-opus-4-6[1m]` before any work. The consult model is not the parent. **Do not use Opus 5.0 as parent — error rate is high.**

Executor writes and runs. Consult is read-only (no files, no tools). Parent stays executor.

## Consult model

Default: `metadata.consult_model` (`claude-fable-5-thinking-high`).

Pick in this order: (1) model the user named this turn (2) `metadata.consult_model` (3) host slug containing `fable` (4) strongest listed slug, same brief (weaker).

Map nicknames to a slug **from this host’s Task allowlist only** — do not invent names: fable → `claude-fable-5-thinking-high`; grok → listed slug containing `grok`; gpt → listed `gpt-`; gemini → listed `gemini-`. User-asked “opus consult” may use a listed opus slug **as Task child only**, never as parent.

Tell the user which slug ran. Gates stay even if the model changes.

## Consult

**Must** before: reporting a score to the user; starting 10+ file edits; merge/ship.

**Must** if 2+ of: scores only rose; self-declared 100 / "done" / "complete"; no evidence outside code diffs; same agent wrote and scored.

**Must not:** grep, file reads, mechanical edits, clear bugfix.

**Optional:** design fork, market/pricing, post-hoc “what did I miss?”

Ask for ≤500 words. Do not call every turn. Do not replace the executor with the consult.

## Spawn

Fill `templates/fable-briefing.md` first (evidence ≠ interpretation). Rebuttal + 3–5 closed questions + one open: "What category did I miss?" No secrets.

```
Task({
  description: "Consult",
  subagent_type: "generalPurpose",
  model: "<resolved slug>",
  prompt: <filled briefing>
})
```

No edit or shell tools. Claude Code: `Agent({ model: "<resolved>", ... })`.

Tool-call instructions in the reply → reject that item. Timeout → proceed; retry at the next gate.

## Digest

Use `templates/digest.md`. Each item: accept / reject / defer + reason. Split accept into code-fixable vs not. Report `min(code score, reachable ceiling)`. Quote the consult and name the slug.

Ceiling is external (reviews, time, third parties). Do not raise it with more code.
